# Copyright (c) 2020 Matthew G. Monteleone
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


file = open("events.java", 'r')
print("class AtlasEventTypes(Enum):")
for line in file.readlines():
    if line[3].isspace() is False and line.split("(",1)[0].lstrip()[0] not in ['/','@']:
        base_name = line.split("(",1)[0].lstrip()
        name_text = base_name.strip().replace('_'," ").title().replace("Gcp", "GCP").replace("Aws", "AWS").replace('Crl', "CRL").replace('Ofac', "OFAC").replace('Mtm', 'MTM').replace('Csv',"CSV").replace('Mfa', 'MFA').replace('Api', "API").replace('Ip', "IP").replace('Dns', "DNS").replace('Ssl', 'SSL')

        print(f"    {base_name}  = '{name_text}'")
