// iOS-safe interfaces only: no extend(), JavaAdapter or generated subclasses.
var controller = require('controller').create({
    net: Vars.net,
    state: function(){ return Vars.state; },
    paused: Packages.mindustry.core.GameState.State.paused,
    playing: Packages.mindustry.core.GameState.State.playing,
    waiting: function(){ return Vars.netServer.isWaitingForPlayers(); },
    cutscene: function(){ return !Vars.headless && Vars.renderer.isCutscene(); },
    announce: function(message){ Call.sendMessage(message); }
});
function hosting(){ return Vars.net.server() && !Vars.net.client(); }
function updateHost(button){
    button.setDisabled(controller.reason() !== null);
    button.getStyle().imageUp = Vars.state.isPaused() ? Icon.play : Icon.pause;
}
Events.on(ClientLoadEvent, cons(function(){
    if(Vars.mobile){
        var toolbar = Core.scene.find('mobile buttons');
        var pause = toolbar === null ? null : toolbar.find('pause');
        if(pause === null){
            Log.err('Multiplayer pausing: native mobile pause button not found; leaving HUD unchanged.');
            return;
        }
        // Keep the actual built-in button, its original cell, style and touch listener.
        // Replace only its action callback, not Button's internal click handling.
        var listeners = pause.getListeners().copy();
        for(var i = 0; i < listeners.size; i++){
            var listener = listeners.get(i);
            if(listener instanceof Packages.arc.scene.event.ClickListener && listener !== pause.getClickListener()){
                pause.removeListener(listener);
            }
        }
        pause.clicked(run(function(){
            if(hosting()){
                controller.toggle();
            }else if(Vars.net.active()){
                Vars.ui.listfrag.toggle();
            }else if(!Vars.state.rules.pauseDisabled){
                Vars.state.set(Vars.state.isPaused() ? Packages.mindustry.core.GameState.State.playing : Packages.mindustry.core.GameState.State.paused);
            }
        }));
        pause.update(run(function(){
            if(hosting()){
                updateHost(pause);
            }else if(Vars.net.active()){
                pause.setDisabled(false);
                pause.getStyle().imageUp = Icon.players;
            }else{
                pause.setDisabled(Vars.state.rules.pauseDisabled || (Vars.state.isCampaign() && Vars.state.afterGameOver));
                pause.getStyle().imageUp = Vars.state.isPaused() ? Icon.play : Icon.pause;
            }
        }));
        // The host still needs a players-list button, now beside the native controls.
        // Collapse its cell completely for guests and single-player.
        var playersCell = toolbar.button(Icon.players, Styles.clearNonei, run(function(){
            if(hosting()) Vars.ui.listfrag.toggle();
        })).size(65);
        var players = playersCell.get();
        players.name = 'host-pause-players';
        players.visibility = boolp(hosting);
        var wasHosting = null;
        players.update(run(function(){
            var host = hosting();
            if(host !== wasHosting){
                playersCell.width(host ? 65 : 0);
                toolbar.invalidateHierarchy();
                wasHosting = host;
            }
        }));
    }else{
        // Desktop has no mobile toolbar. Retain a small native-style icon control.
        var root = new Table();
        root.name = 'host-pause-root';
        root.setFillParent(true);
        root.top().left().marginTop(150).marginLeft(8);
        root.touchable = Touchable.childrenOnly;
        root.visibility = boolp(function(){
            return hosting() && Vars.state.isGame() && Vars.ui.hudfrag.shown
                && !Vars.control.input.logicHideHud && !Core.scene.hasDialog();
        });
        var button = root.button(Icon.pause, Styles.clearNonei, run(function(){ controller.toggle(); })).size(65).get();
        button.name = 'host-pause-button';
        button.update(run(function(){ updateHost(button); }));
        Core.scene.add(root);
    }
}));
