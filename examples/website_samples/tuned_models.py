# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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
from absl.testing import absltest

import google

import pathlib

samples = pathlib.Path(__file__).parent


class UnitTests(absltest.TestCase):
    def test_tuned_models_create(self):
        # [START tuned_models_create]
        import google.generativeai as genai

        import time

        base_model = "models/gemini-1.5-flash-001-tuning"
        training_data = [
            {"text_input": "1", "output": "2"},
            # ... more examples ...
            # [START_EXCLUDE]
            {"text_input": "3", "output": "4"},
            {"text_input": "-3", "output": "-2"},
            {"text_input": "twenty two", "output": "twenty three"},
            {"text_input": "two hundred", "output": "two hundred one"},
            {"text_input": "ninety nine", "output": "one hundred"},
            {"text_input": "8", "output": "9"},
            {"text_input": "-98", "output": "-97"},
            {"text_input": "1,000", "output": "1,001"},
            {"text_input": "10,100,000", "output": "10,100,001"},
            {"text_input": "thirteen", "output": "fourteen"},
            {"text_input": "eighty", "output": "eighty one"},
            {"text_input": "one", "output": "two"},
            {"text_input": "three", "output": "four"},
            # [END_EXCLUDE]
            {"text_input": "seven", "output": "eight"},
        ]
        operation = genai.create_tuned_model(
            # You can use a tuned model here too. Set `source_model="tunedModels/..."`
            display_name="increment",
            source_model=base_model,
            epoch_count=20,
            batch_size=4,
            learning_rate=0.001,
            training_data=training_data,
        )

        for status in operation.wait_bar():
            time.sleep(10)

        result = operation.result()
        print(result)
        # # You can plot the loss curve with:
        # snapshots = pd.DataFrame(result.tuning_task.snapshots)
        # sns.lineplot(data=snapshots, x='epoch', y='mean_loss')

        model = genai.GenerativeModel(model_name=result.name)
        result = model.generate_content("III")
        print(result.text)  # IV
        # [END tuned_models_create]

    def test_tuned_models_generate_content(self):
        # [START tuned_models_generate_content]
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name="tunedModels/my-increment-model")
        result = model.generate_content("III")
        print(result.text)  # "IV"
        # [END tuned_models_generate_content]

    def test_tuned_models_get(self):
        # [START tuned_models_get]
        import google.generativeai as genai

        model_info = genai.get_model("tunedModels/my-increment-model")
        print(model_info)
        # [END tuned_models_get]

    def test_tuned_models_list(self):
        # [START tuned_models_list]
        import google.generativeai as genai

        for model_info in genai.list_tuned_models():
            print(model_info.name)
        # [END tuned_models_list]

    def test_tuned_models_delete(self):
        import time

        base_model = "models/gemini-1.5-flash-001-tuning"
        training_data = samples / "increment_tuning_data.json"
        try:
            operation = genai.create_tuned_model(
                id="delete-this-model",
                # You can use a tuned model here too. Set `source_model="tunedModels/..."`
                display_name="increment",
                source_model=base_model,
                epoch_count=20,
                batch_size=4,
                learning_rate=0.001,
                training_data=training_data,
            )
        except google.api_core.exceptions.AlreadyExists:
            pass
        else:
            for status in operation.wait_bar():
                time.sleep(10)

        # [START tuned_models_delete]
        import google.generativeai as genai

        model_name = "tunedModels/delete-this-model"
        model_info = genai.get_model(model_name)
        print(model_info)

        # You can pass the model_info or name here.
        genai.delete_tuned_model(model_name)
        # [END tuned_models_delete]

    def test_tuned_models_permissions_create(self):
        # [START tuned_models_permissions_create]
        import google.generativeai as genai

        model_info = genai.get_model("tunedModels/my-increment-model")
        # [START_EXCLUDE]
        for p in model_info.permissions.list():
            if p.role.name != "OWNER":
                p.delete()
        # [END_EXCLUDE]

        public_permission = model_info.permissions.create(
            role="READER",
            grantee_type="EVERYONE",
        )

        group_permission = model_info.permissions.create(
            role="READER",
            # Use "user" for an individual email address.
            grantee_type="group",
            email_address="genai-samples-test-group@googlegroups.com",
        )
        # [END tuned_models_permissions_create]
        public_permission.delete()
        group_permission.delete()

    def test_tuned_models_permissions_list(self):
        # [START tuned_models_permissions_list]
        import google.generativeai as genai

        model_info = genai.get_model("tunedModels/my-increment-model")

        # [START_EXCLUDE]
        for p in model_info.permissions.list():
            if p.role.name != "OWNER":
                p.delete()

        public_permission = model_info.permissions.create(
            role="READER",
            grantee_type="EVERYONE",
        )

        group_permission = model_info.permissions.create(
            role="READER",
            grantee_type="group",
            email_address="genai-samples-test-group@googlegroups.com",
        )
        # [END_EXCLUDE]

        for p in model_info.permissions.list():
            print(p)
        # [END tuned_models_permissions_list]
        public_permission.delete()
        group_permission.delete()

    def test_tuned_models_permissions_get(self):
        # [START tuned_models_permissions_get]
        import google.generativeai as genai

        model_info = genai.get_model("tunedModels/my-increment-model")

        # [START_EXCLUDE]
        for p in model_info.permissions.list():
            if p.role.name != "OWNER":
                p.delete()
        # [END_EXCLUDE]

        public = model_info.permissions.create(
            role="READER",
            grantee_type="EVERYONE",
        )
        print(public)
        name = public.name
        print(name)  # tunedModels/{tunedModel}/permissions/{permission}

        from_name = genai.types.Permissions.get(name)
        print(from_name)
        # [END tuned_models_permissions_get]

    def test_tuned_models_permissions_update(self):
        # [START tuned_models_permissions_update]
        import google.generativeai as genai

        model_info = genai.get_model("tunedModels/my-increment-model")

        # [START_EXCLUDE]
        for p in model_info.permissions.list():
            if p.role.name != "OWNER":
                p.delete()
        # [END_EXCLUDE]

        test_group = model_info.permissions.create(
            role="writer",
            grantee_type="group",
            email_address="genai-samples-test-group@googlegroups.com",
        )

        test_group.update({"role": "READER"})
        # [END tuned_models_permissions_get]

    def test_tuned_models_permission_delete(self):
        # [START tuned_models_permissions_delete]
        import google.generativeai as genai

        model_info = genai.get_model("tunedModels/my-increment-model")
        # [START_EXCLUDE]
        for p in model_info.permissions.list():
            if p.role.name != "OWNER":
                p.delete()
        # [END_EXCLUDE]

        public_permission = model_info.permissions.create(
            role="READER",
            grantee_type="EVERYONE",
        )

        public_permission.delete()
        # [END tuned_models_permissions_delete]


if __name__ == "__main__":
    absltest.main()
