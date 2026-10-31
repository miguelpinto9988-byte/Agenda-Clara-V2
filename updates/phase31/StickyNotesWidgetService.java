package pe.agendaclara.app;

import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;
import android.widget.RemoteViewsService;
import java.util.ArrayList;
import java.util.List;

/** Compatibility collection adapter for Android 8–11 and large note lists. */
public final class StickyNotesWidgetService extends RemoteViewsService {
    @Override public RemoteViewsFactory onGetViewFactory(Intent intent){
        return new Factory(getApplicationContext());
    }
    static final class Factory implements RemoteViewsFactory {
        private final Context context;
        private List<StickyNotesStore.Note> notes=new ArrayList<>();
        Factory(Context context){this.context=context;}
        @Override public void onCreate(){notes=StickyNotesStore.get(context).all();}
        @Override public void onDataSetChanged(){notes=StickyNotesStore.get(context).all();}
        @Override public void onDestroy(){notes.clear();}
        @Override public int getCount(){return notes.size();}
        @Override public RemoteViews getViewAt(int position){
            return position>=0&&position<notes.size()
                    ?StickyNotesWidget.row(context,notes.get(position)):null;
        }
        @Override public RemoteViews getLoadingView(){return null;}
        @Override public int getViewTypeCount(){return 1;}
        @Override public long getItemId(int position){return notes.get(position).id;}
        @Override public boolean hasStableIds(){return true;}
    }
}