package pe.agendaclara.app.graphics

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.unit.dp
import androidx.compose.ui.draw.drawWithCache

/** All effects are deterministic, offline, resolution-independent and require no dependency. */
object AgendaPalette {
    val Blue = Color(0xFF2765F5)
    val Ice = Color(0xFF69B4FF)
    val Ink = Color(0xFF182B52)
    val Surface = Color(0xFFF5F8FF)
    val Border = Color(0xFFD9E6FC)
}

fun Modifier.agendaCardFinish(): Modifier = drawWithCache {
    val brush = Brush.linearGradient(listOf(Color.White, AgendaPalette.Surface))
    val radius = 22.dp.toPx()
    onDrawBehind {
        drawRoundRect(brush, cornerRadius = androidx.compose.ui.geometry.CornerRadius(radius))
        drawRoundRect(AgendaPalette.Border, cornerRadius = androidx.compose.ui.geometry.CornerRadius(radius), style = Stroke(1.dp.toPx()))
    }
}

@Composable
fun AgendaLuminousPlus(modifier: Modifier = Modifier) {
    Canvas(modifier) {
        val center = Offset(size.width / 2f, size.height / 2f)
        val r = size.minDimension * .37f
        drawCircle(Brush.radialGradient(listOf(AgendaPalette.Blue.copy(alpha=.3f),Color.Transparent),center,r*1.4f),r*1.4f,center)
        drawCircle(Brush.linearGradient(listOf(AgendaPalette.Ice,AgendaPalette.Blue,Color(0xFF1841CB))),r,center)
        drawCircle(Color.White.copy(alpha=.6f),r*.9f,center,style=Stroke(1.5.dp.toPx()))
        drawLine(Color.White,Offset(center.x-r*.35f,center.y),Offset(center.x+r*.35f,center.y),3.dp.toPx())
        drawLine(Color.White,Offset(center.x,center.y-r*.35f),Offset(center.x,center.y+r*.35f),3.dp.toPx())
    }
}

@Composable
fun AgendaSparkles(modifier: Modifier = Modifier, intensity: Float = 1f) {
    Canvas(modifier) {
        val positions = listOf(.14f to .28f,.78f to .16f,.89f to .7f,.24f to .85f,.54f to .12f)
        positions.forEachIndexed { index, point ->
            val center=Offset(size.width*point.first,size.height*point.second)
            val r=(if(index%2==0)2.2f else 1.4f)*density
            drawCircle(AgendaPalette.Ice.copy(alpha=(.25f*intensity).coerceIn(0f,1f)),r,center)
        }
    }
}
