/** Test-only launcher. Exercises mobile UI and Rhino's iOS code paths on desktop.
 * This is NOT an iOS emulator, nor part of the distributable mod. */
import arc.backend.sdl.SdlApplication;
import arc.backend.sdl.SdlConfig;
import mindustry.Vars;
import mindustry.core.Version;
import mindustry.desktop.DesktopLauncher;
import mindustry.mod.Scripts;
import rhino.*;

class IosPathLauncher {
    public static void main(String[] args) {
        // Kit.isIos uses this property; set it before Rhino initializes.
        System.setProperty("java.vm.name", "RoboVM-test-path");
        System.setProperty("nodiscord", "true");
        Vars.testMobile = true;
        Version.init();
        Vars.loadLogger();
        SdlConfig config = new SdlConfig();
        config.title = "Host Pause iOS-path test";
        config.width = Integer.parseInt(System.getProperty("test.width", "1024"));
        config.height = Integer.parseInt(System.getProperty("test.height", "768"));
        config.maximized = false;
        config.coreProfile = true;
        config.glVersions = new int[][]{{3, 3}, {3, 2}, {2, 1}, {2, 0}};
        new SdlApplication(new DesktopLauncher(args) {
            @Override public Context getScriptContext() {
                Context context = Context.getCurrentContext();
                if(context == null) context = Context.enter();
                context.setOptimizationLevel(-1); // exactly IOSLauncher behavior
                return context;
            }
            @Override public Scripts createScripts() {
                Scripts scripts = new Scripts();
                // Prove no generated JavaAdapter classes are needed by the mod.
                ScriptableObject.putProperty(scripts.scope, "JavaAdapter", new BaseFunction() {
                    @Override public Object call(Context cx, Scriptable scope, Scriptable self, Object[] args) {
                        throw new IllegalStateException("JavaAdapter forbidden in iOS-path test");
                    }
                    @Override public Scriptable construct(Context cx, Scriptable scope, Object[] args) {
                        throw new IllegalStateException("JavaAdapter forbidden in iOS-path test");
                    }
                });
                System.out.println("IOS_PATH_TEST: interpreter="+scripts.context.getOptimizationLevel()+" proxyPath="+Kit.isIos);
                if(!Kit.isIos || scripts.context.getOptimizationLevel() != -1) throw new AssertionError("iOS path not active");
                return scripts;
            }
        }, config);
    }
}
