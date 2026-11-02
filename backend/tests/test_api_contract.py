from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.errors import CalculationValidationErrorResult, DomainErrorResult
from app.schemas.termination import TerminationCalculationResult


client = TestClient(app)
ENDPOINT = "/api/v1/terminations/calculate"


def operation():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()["paths"][ENDPOINT]["post"]


def examples():
    return operation()["requestBody"]["content"]["application/json"]["examples"]


@pytest.mark.parametrize("example_name", [
    "dismissal_without_cause", "resignation", "mutual_agreement",
    "dismissal_with_cause", "worked_notice", "year_boundary_with_previous_payment",
])
def test_published_request_examples_execute_and_match_the_response_schema(example_name):
    response = client.post(ENDPOINT, json=examples()[example_name]["value"])
    assert response.status_code == 200, response.text
    data = response.json()
    result = TerminationCalculationResult.model_validate(data)
    assert result.net_total == (
        result.total - result.inss_total - result.irrf_total
        - result.notice_period_discount - result.thirteenth_settlement.gross_paid
    )
    # O JSON monetário deve continuar decimal em texto, inclusive nos objetos aninhados.
    for name in ("salary_balance", "thirteenth_salary", "total", "net_total", "fgts_penalty"):
        assert isinstance(data[name], str)
        assert Decimal(data[name]).is_finite()
    for item in data["thirteenth_salary_by_year"]:
        assert isinstance(item["value"], str)
    for value in data["thirteenth_settlement"].values():
        assert isinstance(value, str)


def test_documented_success_example_is_the_actual_full_response():
    response = client.post(ENDPOINT, json=examples()["dismissal_without_cause"]["value"])
    assert response.status_code == 200
    documented = operation()["responses"]["200"]["content"]["application/json"]["example"]
    assert response.json() == documented


def test_domain_error_matches_documented_format_and_example():
    payload = {**examples()["resignation"]["value"], "notice_period_type": "indemnified"}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 400
    DomainErrorResult.model_validate(response.json())
    documented = operation()["responses"]["400"]["content"]["application/json"]["example"]
    assert response.json() == documented


def test_unsupported_year_matches_documented_string_error():
    payload = {**examples()["dismissal_without_cause"]["value"], "termination_date": "2027-08-20"}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    error = CalculationValidationErrorResult.model_validate(response.json())
    assert isinstance(error.detail, str)
    documented = operation()["responses"]["422"]["content"]["application/json"]["examples"]["unsupported_year"]["value"]
    assert response.json() == documented


@pytest.mark.parametrize(("field", "value", "issue_type"), [
    ("monthly_salary", "0.00", "greater_than"),
    ("monthly_salary", "NaN", "finite_number"),
    ("termination_type", "unknown", "enum"),
    ("termination_date", "2026-02-30", "date_from_datetime_parsing"),
    ("fgts_rescission_bas", "10000.00", "extra_forbidden"),
])
def test_validation_errors_match_documented_structure(field, value, issue_type):
    payload = {**examples()["dismissal_without_cause"]["value"], field: value}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    error = CalculationValidationErrorResult.model_validate(response.json())
    assert isinstance(error.detail, list)
    assert any(issue.loc == ["body", field] and issue.type == issue_type for issue in error.detail)


def test_zero_salary_error_matches_documented_example():
    payload = {**examples()["dismissal_without_cause"]["value"], "monthly_salary": "0.00"}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    documented = operation()["responses"]["422"]["content"]["application/json"]["examples"]["invalid_input"]["value"]
    assert response.json() == documented


def test_malformed_json_keeps_native_validation_response():
    response = client.post(ENDPOINT, content='{', headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    error = CalculationValidationErrorResult.model_validate(response.json())
    assert any(issue.type == "json_invalid" for issue in error.detail)


def test_required_input_field_is_reported_at_its_location():
    payload = dict(examples()["dismissal_without_cause"]["value"])
    payload.pop("monthly_salary")
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    error = CalculationValidationErrorResult.model_validate(response.json())
    assert any(issue.loc == ["body", "monthly_salary"] and issue.type == "missing" for issue in error.detail)


def test_contract_documents_only_required_inputs_and_rejects_unknown_fields():
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    inputs = schemas["TerminationCalculationInput"]
    assert set(inputs["required"]) == {
        "monthly_salary", "admission_date", "termination_date", "termination_type",
    }
    assert inputs["additionalProperties"] is False
    assert set(operation()["responses"]) == {"200", "400", "422"}


def test_every_result_field_has_a_contract_description():
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    fields = schemas["TerminationCalculationResult"]["properties"]
    assert all(field.get("description") for field in fields.values())


def test_docs_and_health_are_available_without_changing_health_contract():
    assert client.get("/docs").status_code == 200
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
