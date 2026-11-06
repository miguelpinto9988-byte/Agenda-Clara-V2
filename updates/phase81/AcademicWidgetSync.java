package pe.agendaclara.app;

import android.content.Context;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Coalesced background updates after task or schedule changes. */
public final class AcademicWidgetSync {
    private static final ExecutorService EXECUTOR=Executors.newSingleThreadExecutor();
    private static volatile boolean updatePending=false;
    private AcademicWidgetSync(){}
    public static void request(Context context){
        final Context app=context.getApplicationContext();
        synchronized(AcademicWidgetSync.class){
            if(updatePending)return;
            updatePending=true;
        }
        EXECUTOR.execute(()->{
            try{
                AcademicDayWidget.refresh(app);
                AcademicWeekWidget.refresh(app);
            }catch(RuntimeException ignored){
                // Widget providers will be refreshed again by Android's update cycle.
            }finally{
                synchronized(AcademicWidgetSync.class){updatePending=false;}
            }
        });
    }
}