import requests
import os
import json
from json import decoder

class TFERunnerException(Exception):
    pass

class TFERunner(object):

    def __init__(self, tfe_token, org, workspace):
        self.headers = {
            "Authorization": "Bearer {0}".format(tfe_token),
            "Content-Type": "application/vnd.api+json"}
        self.org_name = org
        self._org = None
        self.workspace_name = workspace
        self._workspace = None

    @property
    def workspace(self):
        if not self._workspace:
            url = "https://app.terraform.io/api/v2/organizations/{0}/workspaces".format(self.org_name)
            try:
                workspaces = requests.get(url, headers=self.headers).json()
                for x in workspaces.get('data'):
                    if x.get('attributes').get('name') == self.workspace_name:
                        self._workspace = x
                        return self._workspace
                else:
                    return None
            except Exception, e:
                raise TFERunnerException(str(e))
        else:
            return self._workspace

    @property
    def last_config(self):
        try:
            url = "https://app.terraform.io/api/v2/workspaces/{0}/configuration-versions".format(self.workspace.get("id"))
            resp = requests.get(url, headers=self.headers)
            return resp.json().get("data").pop()
        
        except IndexError, ie:
            raise TFERunnerException(str(ie))

        except Exception, e:
            raise TFERunnerException(str(e))

    def run(self, workspace, config, message):
        data = {
            "data": {
                "attributes": {
                    "is-destroy": False,
                    "message": message
                },
                "type":"runs",
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": workspace.get("id")
                        }
                    },
                    "configuration-version": {
                        "data": {
                            "type": "configuration-versions",
                            "id": config.get("id")
                        }
                    }
                }
            }
        }
        try:
            resp = requests.post("https://app.terraform.io/api/v2/runs", data=json.dumps(data), headers=self.headers)
            return resp
        except Exception, e:
            raise TFERunnerException(str(e))

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--token', default=os.environ.get("ATLAS_TOKEN"))
    parser.add_option('--org')
    parser.add_option('--workspace')
    parser.add_option('--message')
    opt, args = parser.parse_args()

    tfe_runner = TFERunner(opt.token,
                           opt.org,
                           opt.workspace)

    tfe_runner.run(tfe_runner.workspace, tfe_runner.last_config, opt.message)