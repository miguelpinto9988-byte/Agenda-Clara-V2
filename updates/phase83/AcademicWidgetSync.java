package pe.agendaclara.app;

import android.content.Context;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Refresh widgets from the live stores without dropping concurrent change notifications. */
public final class AcademicWidgetSync {
    private static final ExecutorService EXECUTOR=Executors.newSingleThreadExecutor();
    private static boolean running=false;
    private static boolean dirty=false;
    private AcademicWidgetSync(){}

    public static void request(Context context){
        final Context app=context.getApplicationContext();
        synchronized(AcademicWidgetSync.class){
            dirty=true;
            if(running)return;
            running=true;
        }
        try{
            EXECUTOR.execute(()->{
                for(;;){
                    synchronized(AcademicWidgetSync.class){
                        if(!dirty){
                            running=false;
                            return;
                        }
                        dirty=false;
                    }
                    // A failure in one provider must not prevent the other from refreshing.
                    try{AcademicDayWidget.refresh(app);}catch(RuntimeException ignored){}
                    try{AcademicWeekWidget.refresh(app);}catch(RuntimeException ignored){}
                    // Requests arriving during either refresh mark dirty and run again.
                }
            });
        }catch(RuntimeException failure){
            synchronized(AcademicWidgetSync.class){running=false;}
            throw failure;
        }
    }
}
