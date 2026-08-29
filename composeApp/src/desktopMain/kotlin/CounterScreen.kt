import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp

@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    Column(Modifier.padding(top = 24.dp)) {
        Text("Count: $count", modifier = Modifier.testTag("counter_text"))
        Button(
            onClick = { count++ },
            modifier = Modifier.padding(top = 8.dp).testTag("counter_increment_button")
        ) { Text("Increment") }
    }
}
