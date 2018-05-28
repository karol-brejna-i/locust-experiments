#   Copyright 2018 Karol Brejna
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
FROM grubykarol/locust:0.8.1-py3.6-alpine3.7

RUN    apk --no-cache add --virtual=.build-dep build-base
RUN     apk --no-cache add librdkafka-dev \
     && pip install --no-cache-dir confluent-kafka==0.11.4
RUN      apk del .build-dep \