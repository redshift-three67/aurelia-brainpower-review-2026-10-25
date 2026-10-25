from apps.cli.commands.scan import (
    _build_phase1_cli_option_args,
    _effective_adaptive_top_k,
    _phase1_template_values,
)


def test_phase1_template_values_map_to_personal_profile_axes() -> None:
    assert _phase1_template_values("phase1-default") == {
        "emotion": 0.5,
        "physisch": 0.5,
        "mental": 0.5,
        "astral": 0.5,
    }
    assert _phase1_template_values("personal-balanced") == {
        "emotion": 0.6,
        "physisch": 0.6,
        "mental": 0.6,
        "astral": 0.6,
    }
    assert _phase1_template_values("personal-focused") == {
        "emotion": 0.55,
        "physisch": 0.75,
        "mental": 0.65,
        "astral": 0.45,
    }


def test_phase1_cli_options_forward_entropy_image_and_template() -> None:
    args, env = _build_phase1_cli_option_args(
        profile_template="personal-focused",
        entropy_mode="hybrid",
        image_path="C:/images/client.png",
    )

    assert env == {"ME_ENTROPY_MODE": "hybrid"}
    assert args == [
        "--p-emotion",
        "0.55",
        "--p-physisch",
        "0.75",
        "--p-mental",
        "0.65",
        "--p-astral",
        "0.45",
        "--hybrid-entropy",
        "--image",
        "C:/images/client.png",
    ]


def test_adaptive_limits_reduce_detail_top_k_without_starving_reports() -> None:
    assert _effective_adaptive_top_k(192, top_n=7, adaptive_limits=True) == 112
    assert _effective_adaptive_top_k(64, top_n=7, adaptive_limits=True) == 64
    assert _effective_adaptive_top_k(192, top_n=7, adaptive_limits=False) == 192
