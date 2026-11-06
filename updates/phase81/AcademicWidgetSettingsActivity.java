package pe.agendaclara.app;

import android.app.Activity;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProviderInfo;
import android.content.Intent;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import java.util.List;

/** Launcher configuration: select one existing academic profile per widget instance. */
public final class AcademicWidgetSettingsActivity extends Activity {
    private int widgetId=AppWidgetManager.INVALID_APPWIDGET_ID;
    private int dp(int n){return UiDesign.dp(this,n);}
    private TextView text(String value,int size){
        TextView t=new TextView(this);t.setText(value);t.setTextColor(UiDesign.INK);
        t.setTextSize(size);t.setPadding(0,dp(5),0,dp(5));return t;
    }
    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        setResult(RESULT_CANCELED);
        widgetId=getIntent().getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,
                AppWidgetManager.INVALID_APPWIDGET_ID);
        if(widgetId==AppWidgetManager.INVALID_APPWIDGET_ID){finish();return;}
        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22),dp(26),dp(22),dp(22));
        root.setBackgroundColor(UiDesign.BG);
        TextView heading=text("Configurar widget académico",22);
        heading.setTypeface(null,android.graphics.Typeface.BOLD);
        root.addView(heading);
        root.addView(text("Elige qué horario mostrará este widget. Cada widget puede tener uno diferente.",14));
        List<AcademicSchedules.Profile> profiles=AcademicSchedules.all(this);
        if(profiles.isEmpty()){
            root.addView(text("Todavía no tienes horarios: crea uno en Calendario > Plan de estudio.",14));
            Button close=new Button(this);close.setText("Cerrar");
            close.setOnClickListener(v->finish());root.addView(close);
            setContentView(root);return;
        }
        String[] names=new String[profiles.size()];
        for(int i=0;i<profiles.size();i++)names[i]=profiles.get(i).name;
        Spinner picker=new Spinner(this);
        picker.setAdapter(new ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item,names));
        WidgetAppearance.Settings current=WidgetAppearance.read(this,widgetId);
        for(int i=0;i<profiles.size();i++)if(profiles.get(i).id.equals(current.profileId))
            picker.setSelection(i);
        root.addView(text("Horario académico",16));
        root.addView(picker);
        root.addView(text("Estilo de widget",16));
        Spinner theme=new Spinner(this);
        String[] themeLabels={"Seguir sistema","Claro","Oscuro"};
        theme.setAdapter(new ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item,themeLabels));
        theme.setSelection("light".equals(current.theme)?1:"dark".equals(current.theme)?2:0);
        root.addView(theme);
        CheckBox privacy=new CheckBox(this);
        privacy.setText("Ocultar nombres de cursos y tareas");
        privacy.setTextColor(UiDesign.INK);
        privacy.setChecked(current.hidePrivateTitles);
        root.addView(privacy);
        Button save=new Button(this);
        save.setText("Guardar widget");
        UiDesign.button(save,true);
        LinearLayout.LayoutParams saveParams=new LinearLayout.LayoutParams(-1,dp(54));
        saveParams.topMargin=dp(22);root.addView(save,saveParams);
        save.setOnClickListener(v->{
            String chosen=profiles.get(picker.getSelectedItemPosition()).id;
            String selectedTheme=theme.getSelectedItemPosition()==1?"light":
                    theme.getSelectedItemPosition()==2?"dark":"system";
            WidgetAppearance.save(this,widgetId,new WidgetAppearance.Settings(
                    chosen,selectedTheme,"normal",privacy.isChecked()));
            AppWidgetManager manager=AppWidgetManager.getInstance(this);
            AppWidgetProviderInfo info=manager.getAppWidgetInfo(widgetId);
            if(info==null||info.provider==null){return;}
            String widget=info.provider.getClassName();
            if(AcademicDayWidget.class.getName().equals(widget))
                AcademicDayWidget.update(this,manager,widgetId);
            else if(AcademicWeekWidget.class.getName().equals(widget))
                AcademicWeekWidget.update(this,manager,widgetId);
            else return;
            Intent result=new Intent();
            result.putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,widgetId);
            setResult(RESULT_OK,result);
            finish();
        });
        root.setFocusableInTouchMode(true);
        root.requestFocus();
        setContentView(root);
    }
}