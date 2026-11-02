from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


BASE_PAYLOAD = {
    "monthly_salary": "3000.00",
    "admission_date": "2024-01-10",
    "termination_date": "2026-08-20",
    "acquired_vacation_periods": 1,
    "overdue_vacation_periods": 1,
    "fgts_rescission_base": "10000.00",
}


def test_calculate_termination_without_cause_api() -> None:
    payload = {
        **BASE_PAYLOAD,
        "termination_type": "dismissal_without_cause",
    }

    response = client.post(
        "/api/v1/terminations/calculate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["salary_balance"] == "2000.00"
    assert data["notice_period_days"] == 36
    assert data["notice_period_value"] == "3600.00"
    assert data["projected_termination_date"] == "2026-09-25"

    assert data["thirteenth_salary"] == "2250.00"

    assert data["fgts_penalty"] == "4000.00"

    assert data["total"] == "22850.00"
    assert data["net_total"] == "22516.12"


def test_calculate_resignation_api() -> None:
    payload = {
        **BASE_PAYLOAD,
        "termination_type": "resignation",
    }

    response = client.post(
        "/api/v1/terminations/calculate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["salary_balance"] == "2000.00"

    assert data["notice_period_days"] == 0
    assert data["notice_period_value"] == "0.00"
    assert data["projected_termination_date"] == "2026-08-20"

    assert data["thirteenth_salary"] == "2000.00"

    assert data["vacation_accrued_months"] == 7
    assert data["proportional_vacation"] == "1750.00"
    assert data["proportional_vacation_bonus"] == "583.33"

    assert data["fgts_penalty"] == "0.00"

    assert data["total"] == "18333.33"
    assert data["net_total"] == "18021.95"


def test_calculate_mutual_agreement_api() -> None:
    payload = {
        **BASE_PAYLOAD,
        "termination_type": "mutual_agreement",
    }

    response = client.post(
        "/api/v1/terminations/calculate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["salary_balance"] == "2000.00"

    assert data["notice_period_days"] == 36
    assert data["notice_period_value"] == "1800.00"
    assert data["projected_termination_date"] == "2026-09-25"

    assert data["fgts_penalty"] == "2000.00"

    assert Decimal(data["total"]) > Decimal("0.00")
    assert Decimal(data["net_total"]) > Decimal("0.00")


def test_calculate_dismissal_with_cause_api() -> None:
    payload = {
        **BASE_PAYLOAD,
        "termination_type": "dismissal_with_cause",
    }

    response = client.post(
        "/api/v1/terminations/calculate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["salary_balance"] == "2000.00"

    assert data["notice_period_days"] == 0
    assert data["notice_period_value"] == "0.00"
    assert data["projected_termination_date"] == "2026-08-20"

    assert data["thirteenth_salary"] == "0.00"

    assert data["vacation_accrued_months"] == 0
    assert data["proportional_vacation"] == "0.00"
    assert data["proportional_vacation_bonus"] == "0.00"

    assert data["fgts_penalty"] == "0.00"

    assert data["total"] == "14000.00"


def test_calculate_termination_rejects_invalid_type_api() -> None:
    payload = {
        **BASE_PAYLOAD,
        "termination_type": "INVALID_TYPE",
    }

    response = client.post(
        "/api/v1/terminations/calculate",
        json=payload,
    )

    assert response.status_code == 422