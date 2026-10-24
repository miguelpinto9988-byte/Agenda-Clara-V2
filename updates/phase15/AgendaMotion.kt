package pe.agendaclara.app.motion

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.EnterTransition
import androidx.compose.animation.ExitTransition
import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import android.provider.Settings
import kotlinx.coroutines.delay

/** Reusable, offline motion system. No third-party assets or network. */
object AgendaMotion {
    const val FAST = 140
    const val NORMAL = 240
    const val EXPAND = 300
    const val STAGGER_MS = 48L
    const val HALO_MS = 1600
    val easing = CubicBezierEasing(.2f, 0f, 0f, 1f)
}

/** Honors Android animator duration scale (including animations disabled). */
@Composable
fun rememberMotionEnabled(): Boolean {
    val context = LocalContext.current
    return remember(context) {
        runCatching {
            Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) > 0f
        }.getOrDefault(true)
    }
}

@Composable
fun MotionReveal(
    visible: Boolean,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val enabled = rememberMotionEnabled()
    val enter: EnterTransition = if (enabled)
        fadeIn(tween(AgendaMotion.NORMAL)) + expandVertically(tween(AgendaMotion.EXPAND))
    else EnterTransition.None
    val exit: ExitTransition = if (enabled)
        fadeOut(tween(AgendaMotion.FAST)) + shrinkVertically(tween(AgendaMotion.NORMAL))
    else ExitTransition.None
    AnimatedVisibility(visible = visible, modifier = modifier, enter = enter, exit = exit) {
        content()
    }
}

@Composable
fun StaggeredAction(
    visible: Boolean,
    index: Int,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val enabled = rememberMotionEnabled()
    var entered by remember(index) { mutableStateOf(false) }
    LaunchedEffect(visible, index, enabled) {
        entered = false
        if (visible) {
            if (enabled) delay(index.coerceAtLeast(0) * AgendaMotion.STAGGER_MS)
            entered = true
        }
    }
    val alpha by animateFloatAsState(
        targetValue = if (entered) 1f else 0f,
        animationSpec = tween(if (enabled) AgendaMotion.NORMAL else 0),
        label = "quick-action-alpha"
    )
    val offset by animateFloatAsState(
        targetValue = if (entered) 0f else 26f,
        animationSpec = tween(if (enabled) AgendaMotion.EXPAND else 0, easing = AgendaMotion.easing),
        label = "quick-action-slide"
    )
    val density = LocalDensity.current.density
    Box(modifier.graphicsLayer {
        this.alpha = alpha
        translationX = offset * density
    }) { content() }
}

@Composable
fun PulsingHalo(
    enabled: Boolean = true,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val allowed = rememberMotionEnabled()
    val transition = rememberInfiniteTransition(label = "fab-halo")
    val pulse by transition.animateFloat(
        initialValue = .94f,
        targetValue = 1.12f,
        animationSpec = infiniteRepeatable(
            tween(AgendaMotion.HALO_MS, easing = FastOutSlowInEasing),
            RepeatMode.Reverse
        ),
        label = "halo-scale"
    )
    Box(modifier.graphicsLayer {
        val scale = if (enabled && allowed) pulse else 1f
        scaleX = scale
        scaleY = scale
    }) { content() }
}

@Composable
fun AccordionChevron(
    expanded: Boolean,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val enabled = rememberMotionEnabled()
    val angle by animateFloatAsState(
        targetValue = if (expanded) 180f else 0f,
        animationSpec = tween(if (enabled) AgendaMotion.NORMAL else 0),
        label = "accordion-chevron"
    )
    Box(modifier.graphicsLayer { rotationZ = angle }) { content() }
}
