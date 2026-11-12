#!/usr/bin/env python3
"""Two real v160.7 desktop clients; the guest does not have Host Pause installed."""
import argparse, json, os, pathlib, secrets, shutil, subprocess, tempfile, time
p=argparse.ArgumentParser();p.add_argument('--jar',required=True);p.add_argument('--output',default='test-results');p.add_argument('--ios-path',action='store_true');p.add_argument('--portrait',action='store_true');p.add_argument('--guest-mod',action='store_true');a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1]; out=pathlib.Path(a.output).resolve();out.mkdir(exist_ok=True,parents=True)
work=pathlib.Path(tempfile.mkdtemp(prefix='host-pause-integration-'));procs=[];logs=[]
jar=str(pathlib.Path(a.jar).resolve()); display=150+secrets.randbelow(70);auth=work/'xauth'
config=work/'xorg.conf';config.write_text('''Section "Device"
Identifier "Dummy"
Driver "dummy"
VideoRam 256000
EndSection
Section "Monitor"
Identifier "Monitor"
HorizSync 5.0-1000.0
VertRefresh 5.0-200.0
Modeline "1280x720" 74.5 1280 1344 1472 1664 720 723 728 748
EndSection
Section "Screen"
Identifier "Screen"
Device "Dummy"
Monitor "Monitor"
DefaultDepth 24
SubSection "Display"
Depth 24
Modes "1280x720"
EndSubSection
EndSection
''')
def launch(cmd, logfile, env=None):
 f=open(logfile,'w');logs.append(f);proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env);procs.append(proc);return proc

def await_text(path,needle,timeout=60):
 deadline=time.monotonic()+timeout
 while time.monotonic()<deadline:
  text=path.read_text(errors='replace') if path.exists() else ''
  if needle in text:return text[text.rfind(needle):].splitlines()[0]
  time.sleep(.2)
 raise AssertionError(f'Timed out waiting for {needle!r}; see {path}')

index=0
profiles={}
def call(who,expr):
 global index
 index+=1;marker=f'HP_RESULT_{index}:'
 cmd,log=profiles[who];temp=cmd.with_suffix('.new')
 temp.write_text(f"{json.dumps(marker)} + (function(){{{expr}}})()")
 temp.replace(cmd)
 line=await_text(log,marker)
 value=line.split(marker,1)[1]
 print(who,marker,value,flush=True)
 return value

def prepare(who,mod=False):
 home=work/who;data=home/'.local/share/Mindustry';mods=data/'mods';mods.mkdir(parents=True)
 if mod:
  shutil.copytree(root/'scripts',mods/'host-pause/scripts');shutil.copy(root/'mod.json',mods/'host-pause/mod.json')
 driver=mods/'integration-driver';(driver/'scripts').mkdir(parents=True)
 (driver/'mod.json').write_text(json.dumps(dict(name='integration-driver',version='1',minGameVersion='160.7',hidden=True)))
 cmd=work/f'{who}-command.js';log=out/f'{who}.log';profiles[who]=(cmd,log)
 (driver/'scripts/main.js').write_text('''Events.on(ClientLoadEvent, cons(function(){
 Timer.schedule(run(function(){var f=new Fi(%s);if(f.exists()){var s=f.readString();f.delete();print(Vars.mods.getScripts().runConsole(s));}}),2,0.2);
}));'''%json.dumps(str(cmd)))
 env=os.environ.copy();env.update(DISPLAY=f'127.0.0.1:{display}',XAUTHORITY=str(auth),XDG_DATA_HOME=str(home/'.local/share'),XDG_CACHE_HOME=str(home/'.cache'),HOME=str(home),SDL_AUDIODRIVER='dummy')
 launch(['java',f'-Duser.home={home}','-Dnodiscord=true'] + (['-Dtest.width=768','-Dtest.height=1024'] if a.portrait else []) + (['-cp',jar,str(root/'tests/IosPathLauncher.java')] if a.ios_path else ['-jar',jar]),log,env)
 await_text(log,'Total time to load:')
 if a.ios_path: await_text(log,'IOS_PATH_TEST: interpreter=-1 proxyPath=true')
 return log

try:
 subprocess.run(['xauth','-f',str(auth),'add',f'127.0.0.1:{display}','.',secrets.token_hex(16)],check=True,capture_output=True)
 launch(['Xorg',f':{display}','-auth',str(auth),'-config',str(config),'-logfile',str(out/'xorg.log'),'-noreset','-nolisten','unix','-nolisten','local','-listen','tcp'],out/'xorg-console.log')
 time.sleep(2)
 prepare('host',True)
 assert call('host',"return Vars.mods.locateMod('host-pause').meta.hidden;").startswith('true')
 call('host',"Core.scene.root.getChildren().copy().each(cons(function(e){if(e instanceof Packages.arc.scene.ui.Dialog)e.hide();})); Vars.control.playMap(Vars.maps.all().find(boolf(function(m){return m.name() == 'Maze';})), new Packages.mindustry.game.Rules()); return 'map requested';")
 time.sleep(2)
 if a.ios_path:
  assert call('host',"var b=Core.scene.find('mobile buttons').find('pause');return b !== null && !Core.scene.find('host-pause-players').visible;").startswith('true')
  assert call('host',"Vars.state.set(Packages.mindustry.core.GameState.State.playing);Core.scene.find('mobile buttons').find('pause').fireClick();return Vars.state.isPaused();").startswith('true')
 assert call('host',"Vars.net.host(6571);Vars.player.name='Test Host';Vars.state.set(Packages.mindustry.core.GameState.State.playing);return Vars.net.server() && Vars.state.isGame();").startswith('true')
 time.sleep(8)
 if a.ios_path:
  assert call('host',"var p=Core.scene.find('host-pause-players');var v=p.localToStageCoordinates(new Packages.arc.math.geom.Vec2());return p.visible && p.getWidth()>=44 && v.x+p.getWidth()<=Core.scene.getWidth();").startswith('true')
  call('host',"Core.scene.find('host-pause-players').fireClick();return 'players opened';");time.sleep(.5)
  assert call('host',"return Core.scene.find('playerlist').visible && !Vars.state.isPaused();").startswith('true')
  call('host',"Core.scene.find('host-pause-players').fireClick();return 'players closed';")
 assert call('host',"var b=(Core.scene.find('host-pause-button') || Core.scene.find('mobile buttons').find('pause'));var v=b.localToStageCoordinates(new Packages.arc.math.geom.Vec2());return b.getWidth()>=44 && b.getHeight()>=44 && v.x>=0 && v.y>=0 && v.x+b.getWidth()<=Core.scene.getWidth() && v.y+b.getHeight()<=Core.scene.getHeight();").startswith('true')
 print(call('host',"return 'paused='+Vars.state.isPaused()+' disabled='+(Core.scene.find('host-pause-button') || Core.scene.find('mobile buttons').find('pause')).isDisabled()+' cutscene='+Vars.renderer.isCutscene()+' gameover='+Vars.state.gameOver;"))
 assert call('host',"(Core.scene.find('host-pause-button') || Core.scene.find('mobile buttons').find('pause')).fireClick();return Vars.state.isPaused();").startswith('true')
 tick1=call('host',"return Vars.state.tick;")
 time.sleep(3)
 assert call('host',"return Vars.state.tick;")==tick1
 assert call('host',"return (Core.scene.find('host-pause-button') || Core.scene.find('mobile buttons').find('pause')).getStyle().imageUp == Icon.play;").startswith('true')
 prepare('guest', a.guest_mod)
 call('guest',"Core.scene.root.getChildren().copy().each(cons(function(e){if(e instanceof Packages.arc.scene.ui.Dialog)e.hide();}));Core.settings.put('name','Test Guest');Vars.player.name='Test Guest';Vars.ui.join.connect('127.0.0.1',6571);return 'connecting';")
 await_text(profiles['guest'][1],'Received world data:')
 time.sleep(2)
 assert call('guest',"return Vars.net.client() && Vars.state.isPaused() && (Vars.mods.locateMod('host-pause') !== null) == "+str(a.guest_mod).lower()+";").startswith('true')
 if a.guest_mod and a.ios_path:
  assert call('guest',"return !Core.scene.find('host-pause-players').visible && Core.scene.find('mobile buttons').find('pause').getStyle().imageUp == Icon.players;").startswith('true')
  call('guest',"Core.scene.find('mobile buttons').find('pause').fireClick();return 'guest players';");time.sleep(.5)
  assert call('guest',"return Core.scene.find('playerlist').visible && Vars.state.isPaused();").startswith('true')
  call('guest',"Core.scene.find('mobile buttons').find('pause').fireClick();return 'guest closed';")
 gtick=call('guest',"return Vars.state.tick;");time.sleep(3)
 assert call('guest',"return Vars.state.tick;")==gtick
 call('host',"(Core.scene.find('host-pause-button') || Core.scene.find('mobile buttons').find('pause')).fireClick();return Vars.state.isPaused();")
 time.sleep(2)
 assert call('guest',"return !Vars.state.isPaused() && Vars.state.tick > "+gtick.strip()+";").startswith('true')
 call('host',"(Core.scene.find('host-pause-button') || Core.scene.find('mobile buttons').find('pause')).fireClick();return Vars.state.isPaused();")
 time.sleep(2)
 assert call('guest',"return Vars.state.isPaused();").startswith('true')
 # Guests reconnect while paused; this also checks that the host does not auto-resume.
 call('guest',"Vars.net.disconnect();Vars.state.set(Packages.mindustry.core.GameState.State.menu);return 'disconnected';");time.sleep(1)
 call('guest',"Vars.player.name='Test Guest';Vars.ui.join.connect('127.0.0.1',6571);return 'reconnecting';");time.sleep(4)
 assert call('guest',"return Vars.net.client() && Vars.state.isPaused();").startswith('true')
 # Actual UI respects map rules, and can resume again when the rule is restored.
 call('host',"Vars.state.rules.pauseDisabled=true;return 'rule set';");time.sleep(1)
 assert call('host',"return (Core.scene.find('host-pause-button') || Core.scene.find('mobile buttons').find('pause')).isDisabled();").startswith('true')
 call('host',"Vars.state.rules.pauseDisabled=false;return 'rule restored';");time.sleep(1)
 for who in ['host','guest']:
  call(who,"Packages.arc.util.ScreenUtils.saveScreenshot(new Fi("+json.dumps(str(out/f'{who}-paused.png'))+"));return 'screenshot saved';")
 call('host',"(Core.scene.find('host-pause-button') || Core.scene.find('mobile buttons').find('pause')).fireClick();return 'resumed';");time.sleep(1)
 assert call('guest',"return !Vars.state.isPaused();").startswith('true')
 (out/'RESULT.txt').write_text('PASS: official v160.7; guest_mod='+str(a.guest_mod)+'; ios_path='+str(a.ios_path)+'; checks/actions='+str(index)+'; native UI, paused host/guest, resume/re-pause, reconnect, pause-disabled rule.\n')
 print('PASS',out,flush=True)
finally:
 for proc in reversed(procs):
  if proc.poll() is None:proc.terminate()
 for proc in reversed(procs):
  try:proc.wait(timeout=4)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
 for f in logs:f.close()
 print('Isolated test profiles:',work,flush=True)
