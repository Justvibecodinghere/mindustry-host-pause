'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const create = require('../scripts/controller').create;
function fixture(){
 const f = { host:true, client:false, game:true, waiting:false, cutscene:false, calls:[] };
 const state = {rules:{pauseDisabled:false},gameOver:false,afterGameOver:false,value:'playing',isGame:()=>f.game,isPaused:()=>state.value==='paused',set:v=>state.value=v};
 f.state=state;
 f.controller=create({state:()=>f.state,net:{server:()=>f.host,client:()=>f.client},paused:'paused',playing:'playing',waiting:()=>f.waiting,cutscene:()=>f.cutscene,announce:m=>f.calls.push(m)});
 return f;
}
test('host pauses then resumes using native states',()=>{const f=fixture();assert.equal(f.controller.toggle(),true);assert.equal(f.state.value,'paused');assert.equal(f.controller.toggle(),true);assert.equal(f.state.value,'playing');assert.equal(f.calls.length,2)});
for(const [name,change] of [
 ['guest',f=>{f.host=false;f.client=true}], ['offline',f=>f.host=false],
 ['menu',f=>f.game=false], ['game over',f=>f.state.gameOver=true],
 ['campaign ended',f=>f.state.afterGameOver=true], ['map disallows pause',f=>f.state.rules.pauseDisabled=true],
 ['PvP waiting',f=>f.waiting=true], ['cutscene',f=>f.cutscene=true]
]) test(name+' cannot change state',()=>{const f=fixture();change(f);assert.equal(f.controller.toggle(),false);assert.equal(f.state.value,'playing');assert.equal(f.calls.length,0)});
test('authority is rechecked on every click',()=>{const f=fixture();f.controller.toggle();f.client=true;assert.equal(f.controller.toggle(),false);assert.equal(f.state.value,'paused')});
test('external pause changes are respected',()=>{const f=fixture();f.state.value='paused';f.controller.toggle();assert.equal(f.state.value,'playing')});
test('does not change pauseDisabled or PvP rules',()=>{const f=fixture();f.state.rules.pvpAutoPause=true;const before=JSON.stringify(f.state.rules);f.controller.toggle();f.controller.toggle();assert.equal(JSON.stringify(f.state.rules),before)});

test("reset or new map uses new GameState",()=>{const f=fixture();const old=f.state;f.state={...old,value:"playing",isPaused:()=>f.state.value==="paused",set:v=>f.state.value=v};f.controller.toggle();assert.equal(f.state.value,"paused");assert.equal(old.value,"playing")});
