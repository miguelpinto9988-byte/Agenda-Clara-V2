package pe.agendaclara.app;

import android.content.Context;
import android.content.SharedPreferences;
import java.util.ArrayList;
import java.util.List;

/**
 * Phase 11: explicit task-to-course associations.
 *
 * Separate preferences: never modifies Task, Store SQLite schema, WhatsApp or
 * ScheduleDatabase. Stable Task IDs and normalized course identities are used.
 * No guessing based on a title, and no association is created automatically.
 */
public final class MiDiaCourseLinks {
    private static final String FILE = "mi_dia_course_links_v1";
    private MiDiaCourseLinks() {}

    private static String key(long taskId) { return "task_" + taskId; }

    private static SharedPreferences storage(Context c) {
        return c.getSharedPreferences(FILE, Context.MODE_PRIVATE);
    }

    public static String linkedCourse(Context c, long taskId) {
        if (taskId <= 0) return "";
        return storage(c).getString(key(taskId), "");
    }

    public static boolean assign(Context c, long taskId, String course) {
        if (taskId <= 0 || course == null || Store.get(c).find(taskId) == null) return false;
        String identity = ScheduleCourseColors.identity(course);
        if (identity.isEmpty()) return false;
        boolean courseExists = false;
        for (ScheduleEntry entry : ScheduleDatabase.get(c).all()) {
            if (ScheduleCourseColors.identity(entry.course).equals(identity)) {
                courseExists = true;
                break;
            }
        }
        if (!courseExists) return false;
        return storage(c).edit().putString(key(taskId), identity).commit();
    }

    public static void unlink(Context c, long taskId) {
        if (taskId > 0) storage(c).edit().remove(key(taskId)).apply();
    }

    public static List<Task> forCourse(Context c, String course, List<Task> allTasks) {
        String identity = ScheduleCourseColors.identity(course);
        List<Task> found = new ArrayList<>();
        if (identity.isEmpty() || allTasks == null) return found;
        for (Task task : allTasks) {
            if (task.id > 0 && identity.equals(linkedCourse(c, task.id))) found.add(task);
        }
        return found;
    }
}
