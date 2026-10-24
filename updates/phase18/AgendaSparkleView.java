package pe.agendaclara.app;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Color;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.view.View;

/** Decorative non-interactive sparkles; all geometry scales with density. */
public final class AgendaSparkleView extends View {
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final float[] xs={.12f,.24f,.77f,.88f,.62f,.36f};
    private final float[] ys={.25f,.78f,.16f,.68f,.86f,.12f};
    public AgendaSparkleView(Context context){super(context);setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);setClickable(false);}
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);
        float d=getResources().getDisplayMetrics().density;
        for(int i=0;i<xs.length;i++){
            float x=getWidth()*xs[i],y=getHeight()*ys[i],r=(i%2==0?2.2f:1.4f)*d;
            paint.setShader(new RadialGradient(x,y,r*3f,
                new int[]{0x664ea7ff,0x224ea7ff,Color.TRANSPARENT},null,Shader.TileMode.CLAMP));
            canvas.drawCircle(x,y,r*3f,paint);
        }
        paint.setShader(null);
    }
}
