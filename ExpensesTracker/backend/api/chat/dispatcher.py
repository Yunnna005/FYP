from . import collectors

def collect_context(user_id: str, intent) -> dict:
    context = {}

    if "stats" in intent.needs:
        try:
            context["stats"] = collectors.get_stats(
                user_id=user_id,
                month=intent.params.get("month"),
            )
        except Exception as e:
            context["stats"] = {"error": str(e)}

    if "recommendations" in intent.needs:
        try:
            context["recommendations"] = collectors.get_recommendations(user_id)
        except Exception as e:
            context["recommendations"] = {"error": str(e)}

    if "forecast" in intent.needs:
        try:
            context["forecast"] = collectors.get_forecast(user_id)
        except Exception as e:
            context["forecast"] = {"error": str(e)}

    if "anomalies" in intent.needs:
        try:
            context["anomalies"] = collectors.get_anomalies(user_id)
        except Exception as e:
            context["anomalies"] = {"error": str(e)}

    if "flagged_transactions" in intent.needs:
        try:
            context["flagged_transactions"] = collectors.get_flagged_transactions(user_id)
        except Exception as e:
            context["flagged_transactions"] = {"error": str(e)}

    return context