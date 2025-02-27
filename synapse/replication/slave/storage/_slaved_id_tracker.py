# Copyright 2016 OpenMarket Ltd
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
from typing import List, Optional, Tuple

from synapse.storage.database import LoggingDatabaseConnection
from synapse.storage.util.id_generators import AbstractStreamIdTracker, _load_current_id


class SlavedIdTracker(AbstractStreamIdTracker):
    """Tracks the "current" stream ID of a stream with a single writer.

    See `AbstractStreamIdTracker` for more details.

    Note that this class does not work correctly when there are multiple
    writers.
    """

    def __init__(
        self,
        db_conn: LoggingDatabaseConnection,
        table: str,
        column: str,
        extra_tables: Optional[List[Tuple[str, str]]] = None,
        step: int = 1,
    ):
        self.step = step
        self._current = _load_current_id(db_conn, table, column, step)
        if extra_tables:
            for table, column in extra_tables:
                self.advance(None, _load_current_id(db_conn, table, column))

    def advance(self, instance_name: Optional[str], new_id: int):
        self._current = (max if self.step > 0 else min)(self._current, new_id)

    def get_current_token(self) -> int:
        return self._current

    def get_current_token_for_writer(self, instance_name: str) -> int:
        return self.get_current_token()
