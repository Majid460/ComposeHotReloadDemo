import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.window.rememberWindowState

enum class Screen { Counter, Tasks }

@Composable
fun App() {
    var screen by remember { mutableStateOf(Screen.Counter) }

    MaterialTheme {
        Column(Modifier.fillMaxSize().padding(16.dp)) {
            Row {
                Button(
                    onClick = { screen = Screen.Counter },
                    modifier = Modifier.testTag("nav_counter")
                ) { Text("Counter") }
                Button(
                    onClick = { screen = Screen.Tasks },
                    modifier = Modifier.padding(start = 8.dp).testTag("nav_tasks")
                ) { Text("Tasks") }
            }
            when (screen) {
                Screen.Counter -> CounterScreen()
                Screen.Tasks -> TaskListScreen()
            }
        }
    }
}

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "Compose Hot Reload Demo",
        state = rememberWindowState(width = 420.dp, height = 560.dp)
    ) {
        App()
    }
}
