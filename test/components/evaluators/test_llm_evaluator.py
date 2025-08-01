# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List

import pytest

from haystack import Pipeline
from haystack.components.evaluators import LLMEvaluator
from haystack.components.generators.chat.openai import OpenAIChatGenerator
from haystack.dataclasses.chat_message import ChatMessage


class TestLLMEvaluator:
    def test_init_default(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("predicted_answers", List[str])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
        )
        assert component.instructions == "test-instruction"
        assert component.inputs == [("predicted_answers", List[str])]
        assert component.outputs == ["score"]
        assert component.examples == [
            {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
        ]

        assert isinstance(component._chat_generator, OpenAIChatGenerator)
        assert component._chat_generator.client.api_key == "test-api-key"
        assert component._chat_generator.generation_kwargs == {"response_format": {"type": "json_object"}, "seed": 42}

    def test_init_fail_wo_openai_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="None of the .* environment variables are set"):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[("predicted_answers", List[str])],
                outputs=["score"],
                examples=[
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            )

    def test_init_with_chat_generator(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        chat_generator = OpenAIChatGenerator(generation_kwargs={"custom_key": "custom_value"})
        component = LLMEvaluator(
            instructions="test-instruction",
            chat_generator=chat_generator,
            inputs=[("predicted_answers", List[str])],
            outputs=["custom_score"],
            examples=[
                {"inputs": {"predicted_answers": "answer 1"}, "outputs": {"custom_score": 1}},
                {"inputs": {"predicted_answers": "answer 2"}, "outputs": {"custom_score": 0}},
            ],
        )

        assert component._chat_generator is chat_generator

    def test_init_with_invalid_parameters(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        # Invalid inputs
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs={("predicted_answers", List[str])},
                outputs=["score"],
                examples=[
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            )
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[(List[str], "predicted_answers")],
                outputs=["score"],
                examples=[
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            )
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[List[str]],
                outputs=["score"],
                examples=[
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            )
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs={("predicted_answers", str)},
                outputs=["score"],
                examples=[
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            )

        # Invalid outputs
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[("predicted_answers", List[str])],
                outputs="score",
                examples=[
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            )
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[("predicted_answers", List[str])],
                outputs=[["score"]],
                examples=[
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            )

        # Invalid examples
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[("predicted_answers", List[str])],
                outputs=["score"],
                examples={
                    "inputs": {"predicted_answers": "Damn, this is straight outta hell!!!"},
                    "outputs": {"custom_score": 1},
                },
            )
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[("predicted_answers", List[str])],
                outputs=["score"],
                examples=[
                    [
                        {
                            "inputs": {"predicted_answers": "Damn, this is straight outta hell!!!"},
                            "outputs": {"custom_score": 1},
                        }
                    ]
                ],
            )
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[("predicted_answers", List[str])],
                outputs=["score"],
                examples=[
                    {
                        "wrong_key": {"predicted_answers": "Damn, this is straight outta hell!!!"},
                        "outputs": {"custom_score": 1},
                    }
                ],
            )
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[("predicted_answers", List[str])],
                outputs=["score"],
                examples=[
                    {
                        "inputs": [{"predicted_answers": "Damn, this is straight outta hell!!!"}],
                        "outputs": [{"custom_score": 1}],
                    }
                ],
            )
        with pytest.raises(ValueError):
            LLMEvaluator(
                instructions="test-instruction",
                inputs=[("predicted_answers", List[str])],
                outputs=["score"],
                examples=[{"inputs": {1: "Damn, this is straight outta hell!!!"}, "outputs": {2: 1}}],
            )

    def test_to_dict_default(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        chat_generator = OpenAIChatGenerator(generation_kwargs={"response_format": {"type": "json_object"}, "seed": 42})

        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("predicted_answers", List[str])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
        )
        data = component.to_dict()
        assert data == {
            "type": "haystack.components.evaluators.llm_evaluator.LLMEvaluator",
            "init_parameters": {
                "chat_generator": chat_generator.to_dict(),
                "instructions": "test-instruction",
                "inputs": [["predicted_answers", "typing.List[str]"]],
                "outputs": ["score"],
                "progress_bar": True,
                "examples": [
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            },
        }

    def test_to_dict_with_parameters(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        chat_generator = OpenAIChatGenerator(generation_kwargs={"response_format": {"type": "json_object"}, "seed": 42})

        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("predicted_answers", List[str])],
            outputs=["custom_score"],
            examples=[
                {
                    "inputs": {"predicted_answers": "Damn, this is straight outta hell!!!"},
                    "outputs": {"custom_score": 1},
                },
                {
                    "inputs": {"predicted_answers": "Football is the most popular sport."},
                    "outputs": {"custom_score": 0},
                },
            ],
        )
        data = component.to_dict()
        assert data == {
            "type": "haystack.components.evaluators.llm_evaluator.LLMEvaluator",
            "init_parameters": {
                "chat_generator": chat_generator.to_dict(),
                "instructions": "test-instruction",
                "inputs": [["predicted_answers", "typing.List[str]"]],
                "outputs": ["custom_score"],
                "progress_bar": True,
                "examples": [
                    {
                        "inputs": {"predicted_answers": "Damn, this is straight outta hell!!!"},
                        "outputs": {"custom_score": 1},
                    },
                    {
                        "inputs": {"predicted_answers": "Football is the most popular sport."},
                        "outputs": {"custom_score": 0},
                    },
                ],
            },
        }

    def test_from_dict(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        chat_generator = OpenAIChatGenerator(generation_kwargs={"response_format": {"type": "json_object"}, "seed": 42})

        data = {
            "type": "haystack.components.evaluators.llm_evaluator.LLMEvaluator",
            "init_parameters": {
                "chat_generator": chat_generator.to_dict(),
                "instructions": "test-instruction",
                "inputs": [["predicted_answers", "typing.List[str]"]],
                "outputs": ["score"],
                "examples": [
                    {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
                ],
            },
        }

        component = LLMEvaluator.from_dict(data)
        assert isinstance(component._chat_generator, OpenAIChatGenerator)
        assert component._chat_generator.client.api_key == "test-api-key"
        assert component._chat_generator.generation_kwargs == {"response_format": {"type": "json_object"}, "seed": 42}
        assert component.instructions == "test-instruction"
        assert component.inputs == [("predicted_answers", List[str])]
        assert component.outputs == ["score"]
        assert component.examples == [
            {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
        ]

    def test_pipeline_serde(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        pipeline = Pipeline()
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("questions", List[str]), ("predicted_answers", List[List[str]])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
        )
        pipeline.add_component("evaluator", component)
        serialized_pipeline = pipeline.dumps()
        deserialized_pipeline = Pipeline.loads(serialized_pipeline)
        assert deserialized_pipeline == pipeline

    def test_run_with_different_lengths(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("questions", List[str]), ("predicted_answers", List[List[str]])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
        )

        def chat_generator_run(self, *args, **kwargs):
            return {"replies": [ChatMessage.from_assistant('{"score": 0.5}')]}

        monkeypatch.setattr("haystack.components.evaluators.llm_evaluator.OpenAIChatGenerator.run", chat_generator_run)

        with pytest.raises(ValueError):
            component.run(questions=["What is the capital of Germany?"], predicted_answers=[["Berlin"], ["Paris"]])

        with pytest.raises(ValueError):
            component.run(
                questions=["What is the capital of Germany?", "What is the capital of France?"],
                predicted_answers=[["Berlin"]],
            )

    def test_run_returns_parsed_result(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("questions", List[str]), ("predicted_answers", List[List[str]])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
        )

        def chat_generator_run(self, *args, **kwargs):
            return {"replies": [ChatMessage.from_assistant('{"score": 0.5}')]}

        monkeypatch.setattr("haystack.components.evaluators.llm_evaluator.OpenAIChatGenerator.run", chat_generator_run)

        results = component.run(questions=["What is the capital of Germany?"], predicted_answers=["Berlin"])
        assert results == {"results": [{"score": 0.5}], "meta": None}

    def test_prepare_template(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("predicted_answers", List[str])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Damn, this is straight outta hell!!!"}, "outputs": {"score": 1}},
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}},
            ],
        )
        template = component.prepare_template()
        assert (
            template
            == "Instructions:\ntest-instruction\n\nGenerate the response in JSON format with the following keys:"
            '\n["score"]\nConsider the instructions and the examples below to determine those values.\n\n'
            'Examples:\nInputs:\n{"predicted_answers": "Damn, this is straight outta hell!!!"}\nOutputs:'
            '\n{"score": 1}\nInputs:\n{"predicted_answers": "Football is the most popular sport."}\nOutputs:'
            '\n{"score": 0}\n\nInputs:\n{"predicted_answers": {{ predicted_answers }}}\nOutputs:\n'
        )

    def test_invalid_input_parameters(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("predicted_answers", List[str])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
        )
        # None of the expected parameters are received
        with pytest.raises(ValueError):
            component.validate_input_parameters(
                expected={"predicted_answers": List[str]}, received={"questions": List[str]}
            )

        # Only one but not all the expected parameters are received
        with pytest.raises(ValueError):
            component.validate_input_parameters(
                expected={"predicted_answers": List[str], "questions": List[str]}, received={"questions": List[str]}
            )

        # Received inputs are not lists
        with pytest.raises(ValueError):
            component.validate_input_parameters(expected={"questions": List[str]}, received={"questions": str})

    def test_invalid_outputs(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("predicted_answers", List[str])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
        )
        with pytest.raises(ValueError):
            component.is_valid_json_and_has_expected_keys(
                expected=["score", "another_expected_output"], received='{"score": 1.0}'
            )

        with pytest.raises(ValueError):
            component.is_valid_json_and_has_expected_keys(expected=["score"], received='{"wrong_name": 1.0}')

    def test_output_invalid_json_raise_on_failure_false(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("predicted_answers", List[str])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
            raise_on_failure=False,
        )
        assert (
            component.is_valid_json_and_has_expected_keys(expected=["score"], received="some_invalid_json_output")
            is False
        )

    def test_output_invalid_json_raise_on_failure_true(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        component = LLMEvaluator(
            instructions="test-instruction",
            inputs=[("predicted_answers", List[str])],
            outputs=["score"],
            examples=[
                {"inputs": {"predicted_answers": "Football is the most popular sport."}, "outputs": {"score": 0}}
            ],
        )
        with pytest.raises(ValueError):
            component.is_valid_json_and_has_expected_keys(expected=["score"], received="some_invalid_json_output")
