"""Build a local narrated evidence video; never upload or publish it."""
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/video'
WORK=ROOT/'tmp/video'
REG='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'


def run(args):
    subprocess.run(args,check=True,capture_output=True)


def lines(text,font,width):
    result=[];current=''
    for word in text.split():
        trial=(current+' '+word).strip()
        if font.getlength(trial)>width:
            if not current:raise ValueError('Unbreakable word exceeds frame width')
            result.append(current);current=word
        else:current=trial
    if current:result.append(current)
    return result


def paragraph(draw,text,xy,font,width,color,leading):
    x,y=xy
    for line in lines(text,font,width):
        if y+leading>1010:raise ValueError('Text exceeds safe frame height')
        draw.text((x,y),line,font=font,fill=color);y+=leading
    return y


def main():
    scenes=json.loads((OUT/'storyboard.json').read_text())
    WORK.mkdir(parents=True,exist_ok=True)
    durations=[];records=[]
    for i,scene in enumerate(scenes,1):
        frame=Image.new('RGB',(1920,1080),'#F1F6F5');draw=ImageDraw.Draw(frame)
        draw.rectangle((0,0,1920,20),fill='#087F83')
        draw.text((90,70),scene['subtitle'],font=ImageFont.truetype(BOLD,28),fill='#087F83')
        title=ImageFont.truetype(BOLD,62)
        end=paragraph(draw,scene['title'],(90,135),title,1730,'#132B37',76)
        pointfont=ImageFont.truetype(REG,43 if scene.get('screenshot') else 48)
        limit=1120 if scene.get('screenshot') else 1700
        y=max(270,end+45)
        for point in scene['points']:
            draw.ellipse((94,y+18,110,y+34),fill='#087F83')
            y=paragraph(draw,point,(140,y),pointfont,limit-50,'#132B37',59)+28
        if scene.get('screenshot'):
            original=Image.open(ROOT/'artifacts/well_workflow_v1/demo.jpg')
            # Crop the actual result panel, preserving source pixels and aspect ratio.
            shot=original.crop((18,750,607,1510));shot.thumbnail((540,720))
            frame.paste(shot,(1290,240))
            draw.text((1290,970),'Actual captured output (cropped)',font=ImageFont.truetype(REG,22),fill='#526571')
        y=max(y+20,665 if not scene.get('screenshot') else y+20)
        narrationfont=ImageFont.truetype(REG,31 if scene.get('screenshot') else 35)
        paragraph(draw,scene['narration'],(90,y),narrationfont,limit,'#3D5360',43)
        draw.text((90,1030),'Research candidate | Synthetic narration | '+str(i)+' / '+str(len(scenes)),
                  font=ImageFont.truetype(REG,23),fill='#526571')
        png=WORK/f'scene-{i:02}.png';frame.save(png)
        script=WORK/f'scene-{i:02}.txt';script.write_text(scene['narration'])
        aiff=WORK/f'scene-{i:02}.aiff'
        run(['/usr/bin/say','-v','Samantha (English (US))','-r','160','-f',str(script),'-o',str(aiff)])
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration',
                        '-of','default=nw=1:nk=1',str(aiff)],text=True))
        length=duration+1.0
        mp4=WORK/f'scene-{i:02}.mp4'
        run(['ffmpeg','-y','-loglevel','error','-loop','1','-framerate','25','-i',str(png),'-i',str(aiff),
             '-af','apad=pad_dur=1','-t',str(length),'-c:v','libx264','-preset','veryfast','-tune','stillimage',
             '-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-movflags','+faststart',str(mp4)])
        durations.append(length);records.append({'scene':i,'duration':length,'narration':scene['narration']})
        print(f'Scene {i}: {length:.2f}s',flush=True)
    if sum(durations)>=300:raise ValueError('Video exceeds five-minute target')
    listing=WORK/'concat.txt';listing.write_text(''.join(f"file 'scene-{i:02}.mp4'\n" for i in range(1,len(scenes)+1)))
    video=OUT/'zenithsync-review-video.mp4'
    run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(video)])
    actual=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)],text=True))
    if float(actual['format']['duration'])>=300:raise ValueError('Encoded video exceeds limit')
    (OUT/'production-record.json').write_text(json.dumps({'voice':'macOS Samantha, synthetic','requested_rate':160,
        'scenes':records,'ffprobe':actual,'status':'local review candidate; public access and team attribution pending'},indent=2)+'\n')
    (OUT/'transcript.txt').write_text('\n\n'.join(s['title']+'\n'+s['narration'] for s in scenes)+'\n')
    print(video)


if __name__=='__main__':main()
