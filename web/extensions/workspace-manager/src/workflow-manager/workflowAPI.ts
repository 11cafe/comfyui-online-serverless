import { app } from "@/comfyapp";

async function createWorkflow({}: { name: string; json: string }) {
  // create workflow
  //   const filename = file.match(/(?<=workflows\/)[^/]+(?=\.json)/);
  //   const resp = await fetch(`/api/workflow/createWorkflow`, {
  //     method: "POST",
  //     headers: {
  //       "Content-Type": "application/json",
  //     },
  //     body: JSON.stringify({
  //       name: filename,
  //       json: JSON.stringify(graph),
  //       machine_id: this.machine.id,
  //     }),
  //   }).then((res) => res.json());
  //   if (resp.error || !resp.data.id) {
  //     alert(`❌Error saving workflow: ${resp.error}`);
  //     return;
  //   }
  //   setCurWorkflowID(resp.data.id);
  //   graph.extra.workflow_id = resp.data.id;
  //   const comfyworkflow = new ComfyWorkflow(
  //     app.workflowManager,
  //     filename + ".json",
  //     [filename + ".json"],
  //   );
  //   app.workflowManager.setWorkflow(comfyworkflow);
  return;
}

export async function updateWorkflow(id: string, updateData: any) {
  //   const graph = app.graph;
  //   if (!app.graph.extra.workflow_id) {
  //     graph.extra.workflow_id = id;
  //   } else if (graph.extra.workflow_id !== id) {
  //     alert(
  //       `❌Error saving workflow: workspace id mismatch!! URL ID [${id}], Graph ID [${graph.extra.workspace_info.id}]`,
  //     );
  //     return;
  //   }
  const resp = await fetch(`/api/workflow/updateWorkflow`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id,
      updateData,
    }),
  }).then((res) => res.json());
  return resp;
}
