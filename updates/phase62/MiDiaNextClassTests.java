package pe.agendaclara.app;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.Arrays;

/** Headless, pure-Java regressions for phases 10/14; no Android/Gradle. */
public final class MiDiaNextClassTests {
    private MiDiaNextClassTests() {}

    static void verify(boolean yes, String reason) {
        if (!yes) throw new AssertionError(reason);
    }

    static ScheduleEntry session(long id, int day, int start, int end,
                                 String course, boolean enabled) {
        ScheduleEntry s = new ScheduleEntry();
        s.id = id;
        s.day = day;
        s.start = start;
        s.end = end;
        s.course = course;
        s.enabled = enabled;
        return s;
    }

    public static void main(String[] args) {
        ZoneId lima = ZoneId.of("America/Lima");
        // Monday 2026-11-02, 11:20 local.
        ZonedDateTime clock = ZonedDateTime.of(2026, 11, 2, 11, 20, 0, 0, lima);
        ScheduleEntry current = session(2, 1, 660, 720, "Matemáticas", true);
        ScheduleEntry later = session(3, 1, 780, 840, "Historia", true);
        ScheduleEntry disabled = session(1, 1, 600, 720, "Curso desactivado", false);
        ScheduleEntry invalid = session(9, 1, 750, 740, "Inválido", true);
        MiDiaNextClass.Result result = MiDiaNextClass.choose(
                Arrays.asList(later, disabled, invalid, current), clock);
        verify(result != null && result.inProgress, "A class in progress takes priority");
        verify(result.entry.id == 2, "Choose the actual ongoing class");
        verify(result.dayOffset == 0 && result.minutesUntil == 0, "Ongoing class has 0 minute wait");

        MiDiaNextClass.Result after = MiDiaNextClass.choose(
                Arrays.asList(current, later), clock.plusMinutes(40));
        verify(after != null && !after.inProgress && after.entry.id == 3,
                "At end boundary, class must not be shown as ongoing");
        verify(after.minutesUntil == 60, "Next class is one hour later");

        MiDiaNextClass.Result nextWeek = MiDiaNextClass.choose(
                Arrays.asList(current), clock.plusHours(2));
        verify(nextWeek != null && nextWeek.dayOffset == 7,
                "Same weekday recurring class is scheduled next week");
        verify(nextWeek.entry.id == 2, "Next week's class is selected");

        verify(MiDiaNextClass.choose(new ArrayList<>(), clock) == null,
                "Empty timetable must produce no invented class");
        verify(MiDiaNextClass.choose(Arrays.asList(disabled, invalid), clock) == null,
                "Invalid and disabled classes must never appear");

        ScheduleEntry tomorrow = session(4, 2, 480, 540, "Física", true);
        MiDiaNextClass.Result followingDay = MiDiaNextClass.choose(
                Arrays.asList(later, tomorrow), clock.plusHours(5));
        verify(followingDay != null && followingDay.dayOffset == 1
                && followingDay.entry.id == 4, "Tomorrow's class is correctly found");
        System.out.println("PASS: ongoing class, exact end, next today, next weekday, next week, invalid and empty");
    }
}
