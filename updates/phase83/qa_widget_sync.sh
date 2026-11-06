#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
mkdir -p "$OUT/src/android/content" "$OUT/src/pe/agendaclara/app" "$OUT/classes"
cat > "$OUT/src/android/content/Context.java" <<'JAVA'
package android.content;
public class Context {
    public Context getApplicationContext(){return this;}
}
JAVA
cat > "$OUT/src/pe/agendaclara/app/AcademicDayWidget.java" <<'JAVA'
package pe.agendaclara.app;
import android.content.Context;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
public final class AcademicDayWidget {
    static final AtomicInteger calls=new AtomicInteger();
    static final CountDownLatch started=new CountDownLatch(1);
    static final CountDownLatch unblock=new CountDownLatch(1);
    public static void refresh(Context c){
        int number=calls.incrementAndGet();
        if(number==1){
            started.countDown();
            try{
                if(!unblock.await(6,TimeUnit.SECONDS))
                    throw new IllegalStateException("first refresh timed out");
            }catch(InterruptedException e){
                Thread.currentThread().interrupt();
                throw new IllegalStateException("refresh interrupted",e);
            }
        }
        if(number==2)throw new IllegalStateException("simulated provider failure");
    }
}
JAVA
cat > "$OUT/src/pe/agendaclara/app/AcademicWeekWidget.java" <<'JAVA'
package pe.agendaclara.app;
import android.content.Context;
import java.util.concurrent.atomic.AtomicInteger;
public final class AcademicWeekWidget {
    static final AtomicInteger calls=new AtomicInteger();
    public static void refresh(Context c){calls.incrementAndGet();}
}
JAVA
cat > "$OUT/src/pe/agendaclara/app/AcademicWidgetSyncTests.java" <<'JAVA'
package pe.agendaclara.app;
import android.content.Context;
import java.util.concurrent.TimeUnit;
public final class AcademicWidgetSyncTests {
    public static void main(String[] args) throws Exception {
        int code=1;
        try{
            Context context=new Context();
            AcademicWidgetSync.request(context);
            if(!AcademicDayWidget.started.await(4,TimeUnit.SECONDS))
                throw new AssertionError("First widget refresh never started");
            AcademicWidgetSync.request(context);
            AcademicDayWidget.unblock.countDown();
            long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(8);
            while(System.nanoTime()<deadline &&
                 (AcademicDayWidget.calls.get()<2 || AcademicWeekWidget.calls.get()<2)){
                Thread.sleep(10);
            }
            if(AcademicDayWidget.calls.get()<2)
                throw new AssertionError("Second request was discarded while a widget was refreshing");
            if(AcademicWeekWidget.calls.get()<2)
                throw new AssertionError("A failure in day widget prevented week widget refresh");
            System.out.println("PASS: concurrent data change triggers a second refresh");
            System.out.println("PASS: a failed provider does not block the other widget");
            code=0;
        }finally{System.exit(code);}
    }
}
JAVA
javac -encoding UTF-8 -d "$OUT/classes" \
  "$OUT/src/android/content/Context.java" \
  "$OUT/src/pe/agendaclara/app/AcademicDayWidget.java" \
  "$OUT/src/pe/agendaclara/app/AcademicWeekWidget.java" \
  AgendaClara/app/src/main/java/pe/agendaclara/app/AcademicWidgetSync.java \
  "$OUT/src/pe/agendaclara/app/AcademicWidgetSyncTests.java"
timeout 20s java -cp "$OUT/classes" pe.agendaclara.app.AcademicWidgetSyncTests
