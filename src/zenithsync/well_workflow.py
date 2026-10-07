"""Strict research-only measured-well request to exact additional-well plan."""
import hashlib
import json

import numpy as np

from .contrast_gp import ContrastGP
from .symmetric_design import exact_exchangeable_designs

PARAMETERS = dict(amplitude=1., length=.5, noise_sd=.3, slope=2., correlated=True)


def keys(value, expected, name):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f'{name} requires exactly {sorted(expected)}')


def number(value, name, minimum=0.):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f'{name} must be finite and at least {minimum}')
    try:
        result = float(value)
    except OverflowError as error:
        raise ValueError(f'{name} exceeds floating-point range') from error
    if not np.isfinite(result) or result < minimum:
        raise ValueError(f'{name} must be finite and at least {minimum}')
    return result


def integer(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in [{low}, {high}]')
    return value


def plan_wells(request):
    keys(request, ['schema_version', 'assay_context', 'experiment_id', 'plate_id', 'concentration_unit',
                   'reference_control_id', 'future_control_count', 'additional_wells', 'wells'], 'request')
    integer(request['schema_version'], 'schema_version', 1, 1)
    if request['assay_context'] != 'research_single_agent_organoid':
        raise ValueError('Only the explicitly bounded single-agent organoid research context is supported')
    for field in ['experiment_id', 'plate_id', 'reference_control_id']:
        if not isinstance(request[field], str) or not request[field].strip() or len(request[field]) > 200:
            raise ValueError(f'{field} requires a nonempty identifier of at most 200 characters')
    if request['concentration_unit'] not in ['nM', 'uM']:
        raise ValueError('Concentration unit must be nM or uM; one unit applies to all wells')
    controls_for_prediction = integer(request['future_control_count'], 'future_control_count', 1, 1000)
    wells = request['wells']
    if not isinstance(wells, list) or not 4 <= len(wells) <= 64:
        raise ValueError('Supply 4 to 64 designed wells')
    identifiers, controls, observed = [], [], []
    dose, signal = [], []
    for index, row in enumerate(wells):
        keys(row, ['id', 'kind', 'dose', 'signal'], 'well')
        if (not isinstance(row['id'], str) or not row['id'].strip() or len(row['id']) > 200
                or row['id'] in identifiers):
            raise ValueError('Well identifiers must be distinct nonempty strings of at most 200 characters')
        identifiers.append(row['id'])
        d = number(row['dose'], 'dose')
        if row['kind'] not in ['vehicle_control', 'treatment']:
            raise ValueError('Well kind must be vehicle_control or treatment')
        if (row['kind'] == 'vehicle_control') != (d == 0):
            raise ValueError('Controls have zero drug dose; treatments require positive drug dose')
        if row['kind'] == 'vehicle_control':
            controls.append(index)
        dose.append(d)
        if row['signal'] is None:
            signal.append(None)
        else:
            value = number(row['signal'], 'measured signal')
            if value == 0:
                raise ValueError('Nonpositive raw signals cannot be log transformed; no implicit censoring')
            signal.append(value)
            observed.append(index)
    if request['reference_control_id'] not in identifiers:
        raise ValueError('Reference control is not present in the well design')
    reference = identifiers.index(request['reference_control_id'])
    if reference not in controls or reference not in observed:
        raise ValueError('Reference must be an actually measured vehicle control')
    doses = np.asarray(dose)
    target_doses = np.unique(doses[doses > 0])
    if len(target_doses) < 4:
        raise ValueError('At least four distinct positive drug doses are required')
    if any(not any(doses[i] == d for i in observed) for d in [target_doses[0], target_doses[-1]]):
        raise ValueError('Measure the lowest and highest designed drug doses before planning')
    available = [i for i in range(len(wells)) if i not in observed]
    budget = integer(request['additional_wells'], 'additional_wells', 0, len(available))
    x = np.zeros(len(doses))
    positive = doses > 0
    log_reference = np.log(target_doses[0])
    x[positive] = np.logaddexp(np.log(doses[positive]), log_reference)-log_reference
    x /= x.max()
    targets = np.unique(x[x > 0])
    if len(targets) != len(target_doses):
        raise ValueError('Distinct dose levels are unresolved at coordinate precision')
    n = len(targets)
    others = [i for i in range(len(wells)) if i != reference]
    mapping = {index: n+i for i, index in enumerate(others)}
    model = ContrastGP(**PARAMETERS)
    law = model.joint(targets, x[others])
    measured = [i for i in observed if i != reference]
    contrasts = np.log([signal[i] for i in measured])-np.log(signal[reference])
    posterior = law.condition([mapping[i] for i in measured], contrasts)
    exchangeable = [[mapping[i] for i in available if x[i] == coordinate] for coordinate in np.unique(x[available])]
    exchangeable = [group for group in exchangeable if len(group) > 1]
    result = exact_exchangeable_designs(posterior, range(n), [mapping[i] for i in available],
                                       np.full(n, 1/n), exchangeable, max_representatives=10000)
    selected_joint = result['designs'][budget]['actions']
    inverse = {value: key for key, value in mapping.items()}
    selected = [inverse[i] for i in selected_joint]
    projected = posterior.condition(selected_joint, posterior.mean[list(selected_joint)])
    latent_variance = np.diag(posterior.covariance)[:n]
    future_sd = np.sqrt(np.maximum(latent_variance, 0)+model.noise_sd**2*(1+1/controls_for_prediction))
    predictions = [{'dose': float(d), 'mean_log_response': float(mean),
                    'latent_variance': float(max(0, variance)),
                    'future_contrast_interval90': [float(mean-1.6448536269514722*sd), float(mean+1.6448536269514722*sd)],
                    'expected_latent_variance_after_batch': float(max(0, future_variance))}
                   for d, mean, variance, sd, future_variance in zip(target_doses, posterior.mean[:n], latent_variance,
                       future_sd, np.diag(projected.covariance)[:n], strict=True)]
    return {'schema_version': 1, 'status': 'research_plan', 'experiment_id': request['experiment_id'],
            'plate_id': request['plate_id'], 'concentration_unit': request['concentration_unit'],
            'request_sha256': hashlib.sha256(json.dumps(request, sort_keys=True, allow_nan=False).encode()).hexdigest(),
            'observed_wells': len(observed), 'additional_wells': budget, 'cost_unit': 'one measured well',
            'selected_wells': [{'id': identifiers[i], 'kind': wells[i]['kind'], 'dose': dose[i]} for i in selected],
            'predictions': predictions, 'fixed_parameters': PARAMETERS.copy(),
            'objective': 'mean latent log-response variance over the designed positive doses',
            'variance_reduction': result['designs'][budget]['variance_reduction'],
            'optimization': {k: v for k, v in result.items() if k != 'designs'},
            'uncertainty': {'future_control_count': controls_for_prediction,
                            'meaning': 'fresh treatment log signal minus the mean of fresh control log signals',
                            'calibration': 'model-conditional; nominal 90% intervals were conservative in the frozen cohort'},
            'scope': ['single plate, single drug, positive raw signals',
                      'fixed model assumes independent equal-variance raw log errors',
                      'all supplied unmeasured wells are assumed feasible and equally costly',
                      'batch selection is not a sequential stopping or clinical recommendation',
                      'future observed responses and posterior means after measurement are unknown']}
