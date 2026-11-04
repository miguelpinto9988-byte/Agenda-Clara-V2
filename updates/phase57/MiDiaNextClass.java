package pe.agendaclara.app;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.List;

/** Phase 10: select a live or upcoming recurring class from ScheduleDatabase.
 * Pure Java scheduling logic; no system calendar permissions or network.
 */
public final class MiDiaNextClass {
    private MiDiaNextClass() {}

    public static final class Result {
        public final ScheduleEntry entry;
        public final long beginsAt;
        public final long endsAt;
        public final boolean inProgress;
        public final long minutesUntil;
        public final int dayOffset;

        Result(ScheduleEntry entry, long beginsAt, long endsAt, boolean inProgress,
               long minutesUntil, int dayOffset) {
            this.entry = entry;
            this.beginsAt = beginsAt;
            this.endsAt = endsAt;
            this.inProgress = inProgress;
            this.minutesUntil = minutesUntil;
            this.dayOffset = dayOffset;
        }
    }

    private static long at(LocalDate day, int minutes, ZoneId zone) {
        // ScheduleEntry stores minutes since local midnight; end=1440 is valid.
        LocalDateTime local = day.atStartOfDay().plusMinutes(minutes);
        return local.atZone(zone).toInstant().toEpochMilli();
    }

    /**
     * Show an ongoing class before a future class. If none is ongoing,
     * search the next seven calendar days, including next week's same day.
     * Disabled, malformed and blank sessions are ignored.
     */
    public static Result choose(List<ScheduleEntry> sessions, ZonedDateTime clock) {
        if (sessions == null || sessions.isEmpty()) return null;
        LocalDate today = clock.toLocalDate();
        ZoneId zone = clock.getZone();
        long now = clock.toInstant().toEpochMilli();
        Result current = null, upcoming = null;
        for (int days = 0; days <= 7; days++) {
            LocalDate date = today.plusDays(days);
            int weekday = date.getDayOfWeek().getValue(); // ISO Monday 1 … Sunday 7.
            for (ScheduleEntry classTime : sessions) {
                if (classTime == null || !classTime.enabled ||
                        !ScheduleEntry.valid(classTime) || classTime.day != weekday) continue;
                long start = at(date, classTime.start, zone);
                long end = at(date, classTime.end, zone);
                if (end <= start) continue;
                if (start <= now && now < end) {
                    Result candidate = new Result(classTime, start, end, true, 0, days);
                    if (current == null || candidate.beginsAt < current.beginsAt
                            || (candidate.beginsAt == current.beginsAt
                                && classTime.id < current.entry.id)) current = candidate;
                } else if (start > now) {
                    long minutes = Math.max(1, (start - now + 59999L) / 60000L);
                    Result candidate = new Result(classTime, start, end, false, minutes, days);
                    if (upcoming == null || candidate.beginsAt < upcoming.beginsAt
                            || (candidate.beginsAt == upcoming.beginsAt
                                && classTime.id < upcoming.entry.id)) upcoming = candidate;
                }
            }
        }
        return current != null ? current : upcoming;
    }
}
