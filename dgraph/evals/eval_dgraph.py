from arcade_tdk import ToolCatalog
from arcade_evals import (
    EvalRubric,
    EvalSuite,
    ExpectedToolCall,
    tool_eval,
)
from arcade_evals.critic import SimilarityCritic

import dgraph
from dgraph.tools.dgraph import mutate

# Evaluation rubric
rubric = EvalRubric(
    fail_threshold=0.85,
    warn_threshold=0.95,
)


catalog = ToolCatalog()
catalog.add_module(dgraph)


@tool_eval()
def dgraph_eval_suite() -> EvalSuite:
    suite = EvalSuite(
        name="dgraph Tools Evaluation",
        system_message=(
            "You are an AI assistant with access to dgraph tools. "
            "Use them to help the user with their tasks."
        ),
        catalog=catalog,
        rubric=rubric,
    )

    suite.add_case(
        name="Create a node",
        user_message="Create a node called 'this' with a predicate 'is_a' and object 'test'. Us NQuad format.",
        expected_tool_calls=[ExpectedToolCall(func=mutate, args={"nquads": ['_:this <is_a> "test" .'], "is_delete": False, "json_data": None, "namespace": None})],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="name", weight=0.5),
        ],
    )

    return suite
