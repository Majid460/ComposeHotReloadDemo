import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp

@Composable
fun TaskListScreen() {
    var newTask by remember { mutableStateOf("") }

    // FIX: mutableStateListOf() returns a Compose-observable SnapshotStateList.
    // Mutating it (tasks.add(...)) now correctly notifies Compose, so anything
    // reading `tasks` recomposes immediately.
    val tasks = remember { mutableStateListOf<String>() }

    Column(Modifier.padding(top = 24.dp)) {
        Row {
            OutlinedTextField(
                value = newTask,
                onValueChange = { newTask = it },
                modifier = Modifier.testTag("task_input")
            )
            Button(
                onClick = {
                    if (newTask.isNotBlank()) {
                        tasks.add(newTask)
                    }
                },
                modifier = Modifier.padding(start = 8.dp).testTag("task_add_button")
            ) { Text("Add") }
        }
        Column(
            Modifier.padding(top = 12.dp).testTag("task_list_container")
        ) {
            tasks.forEachIndexed { index, task ->
                Text(task, modifier = Modifier.testTag("task_item_$index"))
            }
        }
    }
}
