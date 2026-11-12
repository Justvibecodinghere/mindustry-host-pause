// No custom packets, rule overrides, or client authority: the host owns game state.
exports.create = function(env){
    function reason(){
        var state = env.state();
        if(!env.net.server() || env.net.client()) return 'Only the host can pause.';
        if(!state.isGame()) return 'No game is running.';
        if(state.gameOver || state.afterGameOver) return 'The game has ended.';
        if(state.rules.pauseDisabled) return 'Pausing is disabled by this map.';
        if(env.waiting()) return 'Waiting for PvP teams; the game controls this pause.';
        if(env.cutscene()) return 'Wait until the cutscene finishes.';
        return null;
    }
    return {
        reason: reason,
        toggle: function(){
            if(reason() !== null) return false;
            var state = env.state();
            var paused = !state.isPaused();
            state.set(paused ? env.paused : env.playing);
            env.announce(paused ? '[accent]Host paused the game.[]' : '[accent]Host resumed the game.[]');
            return true;
        }
    };
};
