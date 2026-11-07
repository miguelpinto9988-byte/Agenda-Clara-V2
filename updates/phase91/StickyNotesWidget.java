package pe.agendaclara.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.TypedValue;
import android.widget.RemoteViews;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;

/** Resizable sticky-note home widget. Independent of deadlines and task completion. */
public final class StickyNotesWidget extends AppWidgetProvider {
    private static final DateTimeFormatter DATE=
            DateTimeFormatter.ofPattern("d MMM yyyy",new Locale("es","PE"));
    /** Paper illustrations follow the saved six-color note preference, not a category. */
    private static int paper(int color,boolean compact){
        switch(color){
            case 1:return compact?R.drawable.ac_notes_horizontal_pink:R.drawable.ac_notes_square_pink;
            case 2:return compact?R.drawable.ac_notes_horizontal_blue:R.drawable.ac_notes_square_blue;
            case 3:return compact?R.drawable.ac_notes_horizontal_green:R.drawable.ac_notes_square_green;
            case 4:return compact?R.drawable.ac_notes_horizontal_purple:R.drawable.ac_notes_square_purple;
            case 5:return compact?R.drawable.ac_notes_horizontal_peach:R.drawable.ac_notes_square_peach;
            default:return compact?R.drawable.ac_notes_horizontal_yellow:R.drawable.ac_notes_square_yellow;
        }
    }
    private static int pin(int color){
        switch(color){
            case 1:return R.drawable.ac_notes_pin_pink;
            case 2:return R.drawable.ac_notes_pin_blue;
            case 3:return R.drawable.ac_notes_pin_green;
            case 4:return R.drawable.ac_notes_pin_purple;
            case 5:return R.drawable.ac_notes_pin_yellow;
            default:return R.drawable.ac_notes_pin_yellow;
        }
    }
    public static RemoteViews row(Context c,StickyNotesStore.Note note){
        return row(c,note,false);
    }
    public static RemoteViews row(Context c,StickyNotesStore.Note note,boolean compact){
        RemoteViews view=new RemoteViews(c.getPackageName(),
            compact?R.layout.widget_notes_board_row_compact:R.layout.widget_notes_board_row);
        view.setImageViewResource(R.id.sticky_widget_art,paper(note.color,compact));
        view.setImageViewResource(R.id.sticky_widget_pin,pin(note.color));
        view.setTextViewText(R.id.sticky_widget_title,note.title);
        view.setTextViewText(R.id.sticky_widget_body,note.body);
        view.setTextViewText(R.id.sticky_widget_date,DATE.format(note.day));
        view.setContentDescription(R.id.sticky_widget_row,
                "Nota adhesiva: "+note.title+". Fecha: "+DATE.format(note.day));
        Intent open=new Intent().putExtra("sticky_note_id",note.id);
        view.setOnClickFillInIntent(R.id.sticky_widget_row,open);
        return view;
    }
    public static void refresh(Context context){
        AppWidgetManager manager=AppWidgetManager.getInstance(context);
        int[] widgetIds=manager.getAppWidgetIds(new ComponentName(context,StickyNotesWidget.class));
        if(widgetIds.length==0)return;
        List<StickyNotesStore.Note> notes=StickyNotesStore.get(context).all();
        for(int widgetId:widgetIds)update(context,manager,widgetId,notes);
    }
    private static void update(Context context,AppWidgetManager manager,int widgetId,
                               List<StickyNotesStore.Note> notes){
        RemoteViews view=new RemoteViews(context.getPackageName(),R.layout.widget_sticky_notes);
        Bundle options=manager.getAppWidgetOptions(widgetId);
        int width=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH,250);
        int height=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,160);
        float scale=context.getResources().getConfiguration().fontScale;
        boolean compact=(width>0&&width<235)||(height>0&&height<170)||scale>=1.3f;
        view=new RemoteViews(context.getPackageName(),
            compact?R.layout.widget_notes_board_compact:R.layout.widget_notes_board);
        view.setTextViewText(R.id.sticky_widget_header,"Notas adhesivas");
        view.setTextViewText(R.id.sticky_widget_count,
                compact?Integer.toString(notes.size()):notes.size()+" notas");
        view.setTextViewText(R.id.sticky_widget_add_label,compact?"＋":"＋ Nota");
        view.setTextViewTextSize(R.id.sticky_widget_header,TypedValue.COMPLEX_UNIT_SP,
                compact?14:17);
        Intent add=new Intent(context,MainActivity.class).setAction("new_sticky_note")
                .setData(Uri.parse("agenda://sticky/add/"+widgetId));
        view.setOnClickPendingIntent(R.id.sticky_widget_add,PendingIntent.getActivity(context,
                41000+widgetId,add,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
        Intent header=new Intent(context,MainActivity.class).setAction("sticky_notes")
                .setData(Uri.parse("agenda://sticky/all/"+widgetId));
        view.setOnClickPendingIntent(R.id.sticky_widget_header,PendingIntent.getActivity(context,
                42000+widgetId,header,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
        Intent template=new Intent(context,MainActivity.class).setAction("sticky_widget_note")
                .setData(Uri.parse("agenda://sticky/open/"+widgetId));
        int flags=PendingIntent.FLAG_UPDATE_CURRENT;
        if(Build.VERSION.SDK_INT>=31)flags|=PendingIntent.FLAG_MUTABLE;
        view.setPendingIntentTemplate(R.id.sticky_widget_list,PendingIntent.getActivity(context,
                43000+widgetId,template,flags));
        if(Build.VERSION.SDK_INT>=31&&notes.size()<=200){
            RemoteViews.RemoteCollectionItems.Builder items=
                    new RemoteViews.RemoteCollectionItems.Builder()
                            .setHasStableIds(true).setViewTypeCount(1);
            for(StickyNotesStore.Note note:notes)items.addItem(note.id,row(context,note,compact));
            view.setRemoteAdapter(R.id.sticky_widget_list,items.build());
        }else{
            Intent service=new Intent(context,StickyNotesWidgetService.class)
                    .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,widgetId)
                    .putExtra("sticky_compact",compact)
                    .setData(Uri.parse("agenda://sticky/service/"+widgetId+"/"+(compact?1:0)));
            view.setRemoteAdapter(R.id.sticky_widget_list,service);
        }
        view.setEmptyView(R.id.sticky_widget_list,R.id.sticky_widget_empty);
        manager.updateAppWidget(widgetId,view);
        if(Build.VERSION.SDK_INT<31||notes.size()>200)
            manager.notifyAppWidgetViewDataChanged(widgetId,R.id.sticky_widget_list);
    }
    @Override public void onUpdate(Context c,AppWidgetManager m,int[] ids){
        List<StickyNotesStore.Note> notes=StickyNotesStore.get(c).all();
        for(int id:ids)update(c,m,id,notes);
    }
    @Override public void onAppWidgetOptionsChanged(Context c,AppWidgetManager m,int id,Bundle opts){
        update(c,m,id,StickyNotesStore.get(c).all());
    }
}