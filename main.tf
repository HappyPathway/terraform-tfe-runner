
data "external" "random_bytes" {
  program = ["python", "${path.module}/scripts/random_output.py"]
}
resource "null_resource" "tfe_runner" {
    provisioner "local-exec" {
        command = "python ${path.module}/scripts/tfe_runner.py --org=${var.tfe_org} --token=${var.tfe_token} --workspace=${var.tfe_workspace} --message='${var.run_message}'"
    }
    triggers = {
        randomness = "${data.external.random_bytes.result["random"]}"
    }
}