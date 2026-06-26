import json
import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.cli.dashboard import (
    build_dashboard_html,
    build_multi_report_dashboard_payload,
    find_latest_report_json,
    find_report_json_files,
    load_report_payload,
    main,
    parse_args,
    write_dashboard_html,
)


class DashboardTest(unittest.TestCase):
    def test_build_dashboard_html_renders_summary_cards_and_top_rows(self) -> None:
        payload = {
            "generated_at": "2026-06-12T12:00:00Z",
            "source": {
                "provider": "youtube",
                "artifact": "data/processed/youtube/sample.json",
            },
            "report_schema_version": 1,
            "records": 1,
            "totals": {
                "views": 100,
                "engagements": 13,
                "engagement_rate_percent": 13.0,
                "average_views_per_record": 100.0,
                "average_engagements_per_record": 13.0,
                "average_likes_per_record": 10.0,
                "average_comments_per_record": 2.0,
                "average_shares_per_record": 1.0,
            },
            "ranking": {"metric": "views", "limit": 5},
            "engagement_breakdown": {
                "likes_percent": 76.92,
                "comments_percent": 15.38,
                "shares_percent": 7.69,
            },
            "data_quality": {"status": "ok", "has_engagements": True},
            "top_content": {"content_id": "video-1"},
            "top_rows": [
                {
                    "content_id": "video-1",
                    "views": 100,
                    "likes": 10,
                    "comments": 2,
                    "shares": 1,
                }
            ],
        }

        html = build_dashboard_html(payload)

        self.assertIn("Social Analytics Dashboard", html)
        self.assertIn('class="dashboard-shell"', html)
        self.assertIn('class="channel-hero"', html)
        self.assertIn("data-visual-dashboard-shell", html)
        self.assertIn("Channel-first analytics", html)
        self.assertIn('class="channel-select"', html)
        self.assertIn('data-channel-manager-open', html)
        self.assertIn('data-channel-manager-list', html)
        self.assertIn('data-channel-manager-add', html)
        self.assertIn('<span>Manage channels</span>', html)
        self.assertNotIn('Channel ID<input name="id"', html)
        self.assertIn('const channelId = form.elements.name.value', html)
        self.assertIn('action: "rename", id: channel.id, name: name.value', html)
        self.assertIn('action: "image"', html)
        self.assertIn("Channel image URL", html)
        self.assertIn("Set image", html)
        self.assertIn('action: enabled ? "disable" : "enable"', html)
        self.assertIn('action: "reference"', html)
        self.assertIn('action: "schedule"', html)
        self.assertIn("Collection schedule", html)
        self.assertIn("YouTube @handle or channel URL", html)
        self.assertIn("Instagram handle or profile URL", html)
        self.assertIn("TikTok handle or profile URL", html)
        self.assertIn("Collect now", html)
        self.assertIn('action: "collect"', html)
        self.assertIn("channel-manager-source-status", html)
        self.assertIn("channel-manager-source-detail", html)
        self.assertIn("platform.status?.status", html)
        self.assertIn("platform.status?.outcome", html)
        self.assertIn("platform.status?.loaded_records", html)
        self.assertIn("platform.status?.last_success", html)
        self.assertIn("source.collection_status", html)
        self.assertIn('class="card metric-card accent"', html)
        self.assertIn('class="metric-spark"', html)
        self.assertIn("Semiannual Performance", html)
        self.assertIn("Productions", html)
        self.assertIn("Followers", html)
        self.assertIn("Unavailable", html)
        self.assertIn("channel-fallback", html)
        self.assertIn("Data updated", html)
        self.assertIn('class="meta freshness"', html)
        self.assertIn('setText("[data-generated-at]", channel.generated_at);', html)
        self.assertIn("2026-06-12 12:00 UTC", html)
        self.assertIn("Semiannual Performance", html)
        self.assertIn("13.00%", html)
        self.assertIn("data-channel-insights", html)
        self.assertIn('class="insight-card content"', html)
        self.assertIn('class="insight-card views"', html)
        self.assertIn('class="insight-card engagement"', html)
        self.assertIn('class="insight-card activity"', html)
        self.assertIn("insight-marker", html)
        self.assertIn('class="insight-marker" aria-hidden="true"', html)
        self.assertIn("data-insight-top-content", html)
        self.assertIn("data-insight-views-leader", html)
        self.assertIn("data-insight-engagement-leader", html)
        self.assertIn("data-insight-production-summary", html)
        self.assertIn("Publishing activity", html)
        self.assertIn("No views leader yet", html)
        self.assertIn("No engagement leader yet", html)
        self.assertIn("Engagement Breakdown", html)
        self.assertIn("76.92%", html)
        self.assertIn("15.38%", html)
        self.assertIn("7.69%", html)
        self.assertIn("Per-Record Averages", html)
        self.assertIn("100.00", html)
        self.assertIn("10.00", html)
        self.assertIn("Report Context", html)
        self.assertIn("Supporting Details", html)
        self.assertIn('data-supporting-details', html)
        self.assertIn("Report schema", html)
        self.assertIn("Ranking by", html)
        self.assertIn("Top items limit", html)
        self.assertIn("views", html)
        self.assertIn("Report file", html)
        self.assertIn("sample.json", html)
        self.assertNotIn("data/processed/youtube/sample.json", html)
        self.assertIn("Data Quality", html)
        self.assertIn("Ready", html)
        self.assertIn("Available", html)
        self.assertIn("video-1", html)
        self.assertIn("1 ranked item", html)
        self.assertIn("Detailed ranking table", html)
        self.assertIn('class="supporting-details"', html)
        self.assertIn("<th>Rank</th>", html)
        self.assertIn('<tr class="winner-row">', html)
        self.assertIn('<span class="rank-badge">#1</span>', html)
        self.assertIn('class="section production-section"', html)
        self.assertIn('class="content-gallery"', html)
        self.assertIn('class="content-card"', html)

    def test_build_dashboard_html_prioritizes_human_content_metadata(self) -> None:
        html = build_dashboard_html(
            {
                "source": {"provider": "youtube", "channel_name": "Brand Channel"},
                "top_content": {
                    "content_id": "video-1",
                    "title": "Launch Review",
                },
                "top_rows": [
                    {
                        "content_id": "video-1",
                        "title": "Launch Review",
                        "thumbnail_url": "https://example.test/thumb.jpg",
                        "content_url": "https://example.test/watch",
                        "content_type": "video",
                        "published_at": "2026-05-20T14:30:00+00:00",
                        "views": 100,
                        "likes": 10,
                        "comments": 2,
                        "shares": 1,
                    }
                ],
            }
        )

        self.assertIn("Launch Review", html)
        self.assertIn('class="content-card-fallback"', html)
        self.assertIn('class="content-thumb fallback"', html)
        self.assertNotIn('src="https://example.test/thumb.jpg"', html)
        self.assertIn('href="https://example.test/watch"', html)
        self.assertIn("May 20, 2026", html)
        self.assertNotIn("ID: video-1", html)

    def test_build_dashboard_html_escapes_text_values(self) -> None:
        html = build_dashboard_html(
            {
                "source": {"provider": "<script>"},
                "generated_at": "<date>",
                "artifact": "<artifact>",
                "ranking": {"metric": "<metric>"},
                "top_content": {"content_id": "<bad>"},
                "top_rows": [{"content_id": "<row>"}],
            }
        )

        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;date&gt;", html)
        self.assertIn("&lt;artifact&gt;", html)
        self.assertIn("&lt;metric&gt;", html)
        self.assertIn("&lt;bad&gt;", html)
        self.assertIn("&lt;row&gt;", html)
        self.assertIn("\\u003cscript\\u003e", html)
        self.assertNotIn("><script>", html)

    def test_build_dashboard_html_renders_unknown_report_metadata(self) -> None:
        html = build_dashboard_html({"source": {"provider": "youtube"}})

        self.assertIn("Report Context", html)
        self.assertIn("YouTube channel", html)
        self.assertIn("unknown", html)
        self.assertIn("Unknown", html)
        self.assertIn("Missing", html)
        self.assertIn("No top content yet", html)
        self.assertIn("No views leader yet", html)
        self.assertIn("No engagement leader yet", html)
        self.assertIn("data-cadence-summary", html)
        self.assertIn("No dates", html)
        self.assertIn("Engagement Breakdown", html)
        self.assertIn("0.00%", html)
        self.assertIn("Per-Record Averages", html)
        self.assertIn("0.00", html)

    def test_build_dashboard_html_uses_top_level_artifact_fallback(self) -> None:
        html = build_dashboard_html(
            {
                "artifact": "data/processed/youtube/fallback.json",
                "source": {"provider": "youtube"},
            }
        )

        self.assertIn("Report file", html)
        self.assertIn("fallback.json", html)
        self.assertNotIn("data/processed/youtube/fallback.json", html)

    def test_build_dashboard_html_renders_multiple_channel_options(self) -> None:
        html = build_dashboard_html(
            {
                "channels": [
                    {
                        "source": {"provider": "youtube", "channel_name": "Channel A"},
                        "records": 2,
                        "totals": {"views": 100},
                    },
                    {
                        "source": {"provider": "youtube", "channel_name": "Channel B"},
                        "records": 3,
                        "totals": {"views": 200},
                    },
                ]
            }
        )

        self.assertIn('<option value="0">Channel A</option>', html)
        self.assertIn('<option value="1">Channel B</option>', html)
        self.assertIn("data-channel-options", html)
        self.assertIn('data-channel-index="0"', html)
        self.assertIn('data-channel-index="1"', html)
        self.assertIn('class="channel-option-card active"', html)
        self.assertIn('"name": "Channel B"', html)
        self.assertIn('"views": "200"', html)

    def test_build_dashboard_html_supports_cross_platform_channel_contract(self) -> None:
        html = build_dashboard_html(
            {
                "channels": [
                    {
                        "source": {
                            "provider": "multi-platform",
                            "channel_name": "Brand Channel",
                        },
                        "records": 8,
                        "top_rows": [
                            {
                                "provider": "youtube",
                                "title": "YouTube winner",
                                "content_url": "https://example.com/youtube-winner",
                                "thumbnail_url": "https://example.com/youtube-thumb.jpg",
                                "content_type": "short",
                                "published_at": "2026-05-20T10:00:00+00:00",
                                "views": 100,
                            },
                            {
                                "provider": "tiktok",
                                "title": "TikTok winner",
                                "content_url": "https://example.com/tiktok-winner",
                                "thumbnail_url": "https://example.com/tiktok-thumb.jpg",
                                "content_type": "video",
                                "published_at": "2026-05-21T10:00:00+00:00",
                                "views": 250,
                            },
                            {
                                "provider": "instagram",
                                "title": "Instagram winner",
                                "content_url": "https://example.com/instagram-winner",
                                "image_url": "https://example.com/instagram-thumb.jpg",
                                "media_type": "reel",
                                "published_at": "2026-05-22T10:00:00+00:00",
                                "views": 150,
                            },
                        ],
                        "platforms": [
                            {
                                "provider": "youtube",
                                "records": 3,
                                "totals": {
                                    "views": 100,
                                    "engagements": 10,
                                    "engagement_rate_percent": 10.0,
                                },
                            },
                            {
                                "provider": "tiktok",
                                "records": 4,
                                "totals": {
                                    "views": 250,
                                    "engagements": 50,
                                    "engagement_rate_percent": 20.0,
                                },
                            },
                            {
                                "provider": "instagram",
                                "records": 1,
                                "totals": {
                                    "views": 150,
                                    "engagements": 15,
                                    "engagement_rate_percent": 10.0,
                                },
                            },
                        ],
                    }
                ]
            }
        )

        self.assertIn('<option value="0">Brand Channel</option>', html)
        self.assertIn("data-channel-preview", html)
        self.assertIn("data-channel-preview-image", html)
        self.assertIn("data-channel-preview-name", html)
        self.assertIn("data-channel-preview-meta", html)
        self.assertIn('"source_summary": "3/3 available sources"', html)
        self.assertIn("3/3 available sources", html)
        self.assertIn('"platforms": [', html)
        self.assertIn('"provider": "youtube"', html)
        self.assertIn('"provider": "tiktok"', html)
        self.assertIn('"provider": "instagram"', html)
        self.assertIn('"views": "500"', html)
        self.assertIn('"engagements": "75"', html)
        self.assertIn('"engagement_rate": "15.00%"', html)
        self.assertIn('"views_share": "20.00%"', html)
        self.assertIn('"views_share": "50.00%"', html)
        self.assertIn('"views_share": "30.00%"', html)
        self.assertIn('"engagements_share": "13.33%"', html)
        self.assertIn('"engagements_share": "66.67%"', html)
        self.assertIn('"engagements_share": "20.00%"', html)
        self.assertIn("View share", html)
        self.assertIn("Engagement share", html)
        self.assertIn('"top_content": "YouTube winner"', html)
        self.assertIn('"top_content": "TikTok winner"', html)
        self.assertIn('"top_content": "Instagram winner"', html)
        self.assertIn('"top_content_url": "https://example.com/youtube-winner"', html)
        self.assertIn('"top_content_url": "https://example.com/tiktok-winner"', html)
        self.assertIn('"top_content_url": "https://example.com/instagram-winner"', html)
        self.assertIn(
            '"top_content_thumbnail_url": "https://example.com/youtube-thumb.jpg"',
            html,
        )
        self.assertIn(
            '"top_content_thumbnail_url": "https://example.com/tiktok-thumb.jpg"',
            html,
        )
        self.assertIn(
            '"top_content_thumbnail_url": "https://example.com/instagram-thumb.jpg"',
            html,
        )
        self.assertIn('"top_content_type": "short"', html)
        self.assertIn('"top_content_type": "video"', html)
        self.assertIn('"top_content_type": "reel"', html)
        self.assertIn('"top_content_views": "100"', html)
        self.assertIn('"top_content_views": "250"', html)
        self.assertIn('"top_content_views": "150"', html)
        self.assertIn('<div class="content-card-fallback">short</div>', html)
        self.assertIn('<div class="content-thumb fallback">short</div>', html)
        self.assertNotIn(
            '<img src="https://example.com/youtube-thumb.jpg" '
            'alt="YouTube winner thumbnail">',
            html,
        )
        self.assertIn(
            '<a href="https://example.com/youtube-winner" target="_blank" '
            'rel="noreferrer">YouTube winner</a>',
            html,
        )
        self.assertIn('"top_content_published_at": "May 20, 2026"', html)
        self.assertIn('"top_content_published_at": "May 21, 2026"', html)
        self.assertIn('"top_content_published_at": "May 22, 2026"', html)
        self.assertIn("Top content", html)
        self.assertIn("Top content type", html)
        self.assertIn("Top content views", html)
        self.assertIn("Top content date", html)
        self.assertIn('"top_views_source": "TikTok (250)"', html)
        self.assertIn('"top_engagement_source": "TikTok (50)"', html)
        self.assertIn("TikTok (250)", html)
        self.assertIn("TikTok (50)", html)
        self.assertIn("Views leader", html)
        self.assertIn("Engagement leader", html)
        self.assertIn('"platform_coverage": "3/3 available"', html)
        self.assertIn("data-platform-coverage", html)
        self.assertIn("3/3 available", html)
        self.assertIn("Platform Sources", html)
        self.assertIn("data-platform-comparison", html)
        self.assertIn('class="platform-chart"', html)
        self.assertIn("Productions</h3>", html)
        self.assertIn('class="platform-chart-fill"', html)
        self.assertIn('<strong>YouTube</strong>', html)
        self.assertIn('<strong>TikTok</strong>', html)
        self.assertIn('<strong>Instagram</strong>', html)

    def test_build_dashboard_html_marks_missing_platform_sources_unavailable(self) -> None:
        html = build_dashboard_html(
            {
                "channels": [
                    {
                        "source": {"provider": "multi-platform", "channel_name": "Partial"},
                        "platforms": [
                            {
                                "provider": "youtube",
                                "records": 1,
                                "totals": {"views": 100, "engagements": 10},
                            }
                        ],
                    }
                ]
            }
        )

        self.assertIn("Platform Sources", html)
        self.assertIn('<strong>YouTube</strong>', html)
        self.assertIn('<strong>TikTok</strong>', html)
        self.assertIn('<strong>Instagram</strong>', html)
        self.assertIn('"platform_coverage": "1/3 available"', html)
        self.assertIn("data-platform-coverage", html)
        self.assertIn("1/3 available", html)
        self.assertIn("No source data for this channel yet.", html)
        self.assertIn("No data", html)

    def test_build_dashboard_html_renders_production_calendar(self) -> None:
        html = build_dashboard_html(
            {
                "source": {"provider": "youtube"},
                "records": 3,
                "production": {
                    "period": "latest_6_months",
                    "date_source": "all_processed_rows",
                    "dates_count": 3,
                },
                "production_dates": [
                    "2026-05-20T14:30:00+00:00",
                    "2026-05-20T16:30:00+00:00",
                    "2026-05-21T14:30:00+00:00",
                ],
            }
        )

        self.assertIn("Production Calendar", html)
        self.assertIn("data-cadence-summary", html)
        self.assertIn('class="cadence-card total"', html)
        self.assertIn('class="cadence-card days"', html)
        self.assertIn('class="cadence-card average"', html)
        self.assertIn('class="cadence-marker" aria-hidden="true"', html)
        self.assertIn("data-cadence-total", html)
        self.assertIn("data-cadence-active-days", html)
        self.assertIn("data-cadence-average", html)
        self.assertIn("Active days", html)
        self.assertIn("Per active day", html)
        self.assertIn("data-production-scope", html)
        self.assertIn("Latest 6 months from all processed content (3 dated item(s))", html)
        self.assertIn(">1.50</strong>", html)
        self.assertIn("3 productions", html)
        self.assertIn("3 productions across 2 day(s)", html)
        self.assertIn("production-day level-", html)
        self.assertIn('"production_days": [', html)

    def test_build_dashboard_html_renders_source_image_url(self) -> None:
        html = build_dashboard_html(
            {
                "source": {
                    "provider": "youtube",
                    "image_url": "https://images.local/channel.png",
                }
            }
        )

        self.assertIn('class="channel-image"', html)
        self.assertIn('src="https://images.local/channel.png"', html)
        self.assertIn('alt="YouTube channel image"', html)

    def test_build_dashboard_html_renders_channel_image_url_alias(self) -> None:
        html = build_dashboard_html(
            {
                "source": {
                    "provider": "youtube",
                    "channel_image_url": "https://images.local/channel-alias.png",
                }
            }
        )

        self.assertIn('src="https://images.local/channel-alias.png"', html)

    def test_build_dashboard_html_uses_fallback_for_placeholder_image_urls(self) -> None:
        html = build_dashboard_html(
            {
                "source": {
                    "provider": "youtube",
                    "image_url": "https://example.com/channel.png",
                },
                "top_rows": [
                    {
                        "title": "Placeholder Thumbnail",
                        "thumbnail_url": "https://example.test/thumb.jpg",
                        "content_type": "short",
                    }
                ],
            }
        )

        self.assertIn("channel-fallback", html)
        self.assertIn('<div class="content-card-fallback">short</div>', html)
        self.assertIn('<div class="content-thumb fallback">short</div>', html)
        self.assertNotIn('src="https://example.com/channel.png"', html)
        self.assertNotIn('src="https://example.test/thumb.jpg"', html)

    def test_build_dashboard_html_renders_empty_top_content_state(self) -> None:
        html = build_dashboard_html(
            {
                "source": {"provider": "youtube"},
                "top_content": {"content_id": "<none>"},
                "top_rows": [],
            }
        )

        self.assertIn("No top content available", html)
        self.assertIn("0 ranked items", html)
        self.assertIn("No top content rows available for this report.", html)
        self.assertIn('td colspan="7"', html)
        self.assertIn('class="empty-row"', html)
        self.assertNotIn("<td>&lt;none&gt;</td><td>0</td><td>0</td>", html)

    def test_load_report_payload_rejects_non_object_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.json"
            report_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "object"):
                load_report_payload(report_path)

    def test_write_dashboard_html_persists_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard" / "index.html"

            path = write_dashboard_html({"records": 0}, output_path)

            self.assertEqual(path, output_path)
            self.assertTrue(path.exists())
            self.assertIn("Social Analytics Dashboard", path.read_text(encoding="utf-8"))

    def test_main_writes_dashboard_from_report_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.json"
            output_path = Path(tmpdir) / "index.html"
            report_path.write_text(json.dumps({"records": 1}), encoding="utf-8")

            exit_code = main(report_path, output_path)

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_main_writes_dashboard_from_multiple_report_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            youtube_path = root / "youtube.json"
            tiktok_path = root / "tiktok.json"
            output_path = root / "index.html"
            youtube_path.write_text(
                json.dumps(
                    {
                        "generated_at": "2026-06-12T12:00:00Z",
                        "source": {
                            "provider": "youtube",
                            "channel_name": "Brand Channel",
                        },
                        "records": 2,
                        "totals": {"views": 100, "engagements": 10},
                    }
                ),
                encoding="utf-8",
            )
            tiktok_path.write_text(
                json.dumps(
                    {
                        "generated_at": "2026-06-13T12:00:00Z",
                        "source": {
                            "provider": "tiktok",
                            "channel_name": "Brand Channel",
                        },
                        "records": 3,
                        "totals": {"views": 200, "engagements": 30},
                    }
                ),
                encoding="utf-8",
            )

            exit_code = main([youtube_path, tiktok_path], output_path)

            html = output_path.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn('<option value="0">Brand Channel</option>', html)
            self.assertIn('"provider": "youtube"', html)
            self.assertIn('"provider": "tiktok"', html)
            self.assertIn('"views": "300"', html)
            self.assertIn('"engagements": "40"', html)

    def test_main_applies_channel_identity_config_to_single_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            report_path = root / "youtube.json"
            config_path = root / "channels.json"
            output_path = root / "index.html"
            report_path.write_text(
                json.dumps(
                    {
                        "source": {
                            "provider": "youtube",
                            "channel_handle": "@brand",
                        },
                        "records": 1,
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {
                                "id": "brand",
                                "display_name": "Configured Brand",
                                "image_url": "https://images.local/brand.png",
                                "platforms": {"youtube": {"handle": "@brand"}},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            exit_code = main(report_path, output_path, channels_config_path=config_path)

            html = output_path.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn('<option value="0">Configured Brand</option>', html)
            self.assertIn('src="https://images.local/brand.png"', html)

    def test_multi_report_dashboard_payload_applies_channel_identity_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {
                                "id": "brand",
                                "display_name": "Configured Brand",
                                "platforms": {
                                    "youtube": {"handle": "@brand"},
                                    "instagram": {"handle": "@brand"},
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            from social_analytics_pipeline.config import load_channel_identity_config

            channels_config = load_channel_identity_config(config_path)

            payload = build_multi_report_dashboard_payload(
                [
                    {
                        "source": {
                            "provider": "youtube",
                            "channel_handle": "@brand",
                        },
                        "records": 1,
                    },
                    {
                        "source": {
                            "provider": "instagram",
                            "channel_handle": "@brand",
                        },
                        "records": 1,
                    },
                ],
                channels_config,
            )

            self.assertEqual(len(payload["channels"]), 1)
            self.assertEqual(payload["channels"][0]["source"]["channel_name"], "Configured Brand")

    def test_build_multi_report_dashboard_payload_groups_by_channel_identity(self) -> None:
        payload = build_multi_report_dashboard_payload(
            [
                {
                    "source": {"provider": "youtube", "channel_handle": "@brand"},
                    "records": 1,
                    "totals": {"views": 100},
                },
                {
                    "source": {"provider": "instagram", "channel_handle": "@brand"},
                    "records": 2,
                    "totals": {"views": 150},
                },
                {
                    "source": {"provider": "youtube", "channel_handle": "@other"},
                    "records": 3,
                    "totals": {"views": 250},
                },
            ]
        )

        self.assertEqual(len(payload["channels"]), 2)
        self.assertEqual(payload["channels"][0]["records"], 3)
        self.assertEqual(len(payload["channels"][0]["platforms"]), 2)
        self.assertEqual(payload["channels"][1]["records"], 3)

    def test_build_multi_report_dashboard_payload_sorts_combined_top_rows(self) -> None:
        payload = build_multi_report_dashboard_payload(
            [
                {
                    "source": {"provider": "instagram", "channel_handle": "@brand"},
                    "records": 1,
                    "ranking": {"metric": "views", "limit": 5},
                    "top_rows": [
                        {"content_id": "ig-1", "title": "Instagram post", "views": 300}
                    ],
                },
                {
                    "source": {"provider": "youtube", "channel_handle": "@brand"},
                    "records": 1,
                    "ranking": {"metric": "views", "limit": 5},
                    "top_rows": [
                        {"content_id": "yt-1", "title": "YouTube video", "views": 900}
                    ],
                },
            ]
        )

        channel = payload["channels"][0]
        self.assertEqual(channel["top_rows"][0]["content_id"], "yt-1")
        self.assertEqual(channel["top_rows"][0]["provider"], "youtube")
        self.assertEqual(channel["top_content"]["content_id"], "yt-1")

    def test_build_multi_report_dashboard_payload_preserves_complete_production_dates(
        self,
    ) -> None:
        payload = build_multi_report_dashboard_payload(
            [
                {
                    "source": {"provider": "instagram", "channel_handle": "@brand"},
                    "records": 1,
                    "production_dates": [
                        "2026-01-01T10:00:00+00:00",
                        "2026-01-02T10:00:00+00:00",
                    ],
                    "top_rows": [{"content_id": "ig-1", "views": 300}],
                },
                {
                    "source": {"provider": "youtube", "channel_handle": "@brand"},
                    "records": 1,
                    "production_dates": ["2026-01-03T10:00:00+00:00"],
                    "top_rows": [{"content_id": "yt-1", "views": 900}],
                },
            ]
        )

        channel = payload["channels"][0]
        self.assertEqual(len(channel["top_rows"]), 2)
        self.assertEqual(
            channel["production_dates"],
            [
                "2026-01-01T10:00:00+00:00",
                "2026-01-02T10:00:00+00:00",
                "2026-01-03T10:00:00+00:00",
            ],
        )
        self.assertEqual(channel["production"]["dates_count"], 3)
        self.assertEqual(channel["production"]["date_source"], "all_processed_rows")

    def test_build_dashboard_html_shows_top_content_platform_metadata(self) -> None:
        html = build_dashboard_html(
            {
                "source": {"provider": "multi-platform", "channel_name": "Brand"},
                "top_rows": [
                    {
                        "content_id": "yt-1",
                        "title": "YouTube video",
                        "provider": "youtube",
                        "views": 900,
                    }
                ],
            }
        )

        self.assertIn("Platform: YouTube", html)
        self.assertNotIn("ID: yt-1", html)

    def test_find_latest_report_json_uses_sorted_latest_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_dir = project_root / "data" / "reports" / "youtube-json"
            report_dir.mkdir(parents=True)
            older = report_dir / "youtube-20260501.json"
            newer = report_dir / "youtube-20260502.json"
            older.write_text("{}", encoding="utf-8")
            newer.write_text("{}", encoding="utf-8")

            self.assertEqual(find_latest_report_json(project_root), newer)

    def test_find_report_json_files_uses_sorted_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            youtube_dir = project_root / "data" / "reports" / "youtube-json"
            instagram_dir = project_root / "data" / "reports" / "instagram-json"
            youtube_dir.mkdir(parents=True)
            instagram_dir.mkdir(parents=True)
            first = instagram_dir / "instagram-20260501.json"
            second = youtube_dir / "youtube-20260502.json"
            second.write_text("{}", encoding="utf-8")
            first.write_text("{}", encoding="utf-8")

            self.assertEqual(find_report_json_files(project_root), [first, second])

    def test_find_latest_report_json_fails_when_missing(self) -> None:
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            self.assertRaisesRegex(RuntimeError, "No report JSON"),
        ):
            find_latest_report_json(Path(tmpdir))

    def test_main_defaults_to_latest_report_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_dir = project_root / "data" / "reports" / "youtube-json"
            report_dir.mkdir(parents=True)
            report_path = report_dir / "youtube-20260502.json"
            output_path = project_root / "dashboard.html"
            report_path.write_text(json.dumps({"records": 1}), encoding="utf-8")

            exit_code = main(output_path=output_path, project_root=project_root)

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_main_all_reports_discovers_report_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_dir = project_root / "data" / "reports" / "youtube-json"
            report_dir.mkdir(parents=True)
            youtube_path = report_dir / "youtube-20260501.json"
            tiktok_path = report_dir / "tiktok-20260501.json"
            output_path = project_root / "dashboard.html"
            youtube_path.write_text(
                json.dumps(
                    {
                        "source": {
                            "provider": "youtube",
                            "channel_name": "Brand Channel",
                        },
                        "records": 1,
                    }
                ),
                encoding="utf-8",
            )
            tiktok_path.write_text(
                json.dumps(
                    {
                        "source": {
                            "provider": "tiktok",
                            "channel_name": "Brand Channel",
                        },
                        "records": 1,
                    }
                ),
                encoding="utf-8",
            )

            exit_code = main(
                output_path=output_path,
                project_root=project_root,
                all_reports=True,
            )

            html = output_path.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn('"provider": "youtube"', html)
            self.assertIn('"provider": "tiktok"', html)

    def test_parse_args_accepts_optional_report_json_and_output(self) -> None:
        args = parse_args(
            [
                "--report-json",
                "report.json",
                "--output",
                "dashboard.html",
                "--project-root",
                "workspace",
                "--channels-config",
                "config/channels.local.json",
            ]
        )

        self.assertEqual(args.report_json, [Path("report.json")])
        self.assertEqual(args.output, Path("dashboard.html"))
        self.assertEqual(args.project_root, Path("workspace"))
        self.assertEqual(args.channels_config, Path("config/channels.local.json"))
        self.assertFalse(args.all_reports)

    def test_parse_args_accepts_multiple_report_json_files(self) -> None:
        args = parse_args(
            [
                "--report-json",
                "youtube.json",
                "--report-json",
                "tiktok.json",
            ]
        )

        self.assertEqual(args.report_json, [Path("youtube.json"), Path("tiktok.json")])

    def test_parse_args_accepts_all_reports(self) -> None:
        args = parse_args(["--all-reports"])

        self.assertTrue(args.all_reports)
        self.assertIsNone(args.report_json)

    def test_parse_args_allows_default_report_json(self) -> None:
        args = parse_args([])

        self.assertIsNone(args.report_json)
        self.assertFalse(args.all_reports)


if __name__ == "__main__":
    unittest.main()
