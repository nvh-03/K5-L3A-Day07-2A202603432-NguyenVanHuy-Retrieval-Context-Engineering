# Định dạng dữ liệu

Các file `example_*.json` chỉ minh họa định dạng, không đủ để nộp bài. Dữ liệu thật là JSON array UTF-8; nếu dùng định dạng khác, ghi cách chuyển trong README.

## Dữ liệu nhập từ Day 6

- [`day6_chunks.json`](day6_chunks.json): 288 paragraph chunks, tạo bằng chunker strategy B của repo Day 6 (`max_size=500`).
- [`day6_questions.json`](day6_questions.json): 20 câu từ `benchmark/questions.json` của Day 6, đã đổi schema, cộng 4 câu kiểm tra thiếu bằng chứng. Tổng cộng 17 câu dev (15 có đáp án, 2 thiếu bằng chứng) và 7 câu test (5 có đáp án, 2 thiếu bằng chứng).
- [`day7_independent_test_questions.json`](day7_independent_test_questions.json): bộ test bổ sung, độc lập với câu hỏi Day 6, gồm 5 câu có đáp án và 2 câu thiếu bằng chứng trên cùng tài liệu/corpus. Có `retrieval_query_en` được dịch chỉ từ câu hỏi để đánh giá pipeline lexical đã chọn. Chưa dùng bộ này để chọn hoặc điều chỉnh cấu hình; chỉ chạy sau khi chốt pipeline.
- Các câu dev có thêm `retrieval_query_en`, bản dịch câu hỏi sang tiếng Anh chỉ để thử query rewriting. Câu hỏi gốc, gold và test không thay đổi; dùng riêng với `retrieval_benchmark.py --query-field retrieval_query_en`.

Nguồn là bài báo “RF Energy-Harvesting Techniques: Applications, Recent Developments, Challenges, and Future Opportunities” của Stella N. Arinze, Emenike Raymond Obi, Solomon H. Ebenuwa và Augustine O. Nwajana, DOI [10.3390/telecom6030045](https://doi.org/10.3390/telecom6030045), được ghi nhận trong manifest Day 6 dưới CC BY 4.0. SHA-256 PDF: `2f2f6d7905e9c9df70a4d58ca24a89a7271e2e16ae4c553594813286e9eb2d72`.

Repo Day 6 không lưu toàn bộ chunks thành JSON; các trace chỉ chứa top-3 kết quả. Vì vậy, chunks ở đây được tái tạo từ PDF Day 6 thật bằng chunker của pipeline B, không phải dữ liệu mẫu và cũng không phải bản dump trực tiếp từ PostgreSQL. Bốn evidence quote dài/cắt qua ranh giới chunk được rút thành trích đoạn nằm nguyên vẹn trong chunk; quote Day 6 gốc được giữ ở trường `day6_evidence_quote` để đối chiếu.

Chạy thử baseline trên dev từ thư mục gốc:

```bash
python starter/baseline.py --chunks data/day6_chunks.json --questions data/day6_questions.json --split dev --output starter/results/day6-export-dev
```

Sau khi chốt cấu hình, chạy bộ test độc lập bổ sung bằng query tiếng Anh mà không dùng kết quả để chỉnh hệ thống:

```bash
python starter/retrieval_benchmark.py --chunks data/day6_chunks.json --questions data/day7_independent_test_questions.json --split test --output starter/results/independent-test-retrieval --methods lexical --query-field retrieval_query_en
python starter/run_agent.py --chunks data/day6_chunks.json --questions data/day7_independent_test_questions.json --split test --output starter/results/independent-test-agent-lexical --method lexical --top-k 3 --max-searches 4 --budget 2000
```

- **Chunk:** `id`, `text`, `source_id`, `source`, `page`, `metadata`. ID phải duy nhất; giữ phiên bản hoặc ngày nếu có.
- **Câu có đáp án:** `id`, `split` (`dev` hoặc `test`), `question`, `expected_answer`, `gold`: danh sách `{source_id, page, evidence}`. Với schema mẫu, mỗi evidence phải nằm trọn trong một chunk đúng nguồn và trang; các phần tử `gold` là evidence thay thế. Với câu multi-hop cần nhiều đoạn, bạn có thể mở rộng schema, ghi rõ nhóm evidence bắt buộc và cách chấm. Có thể thêm `filter` do người dùng cung cấp trước.
- **Câu thiếu evidence:** `id`, `split`, `question`, `answerable: false`, `expected_behavior: "search_and_abstain"`, `absence_reason`. Xem `agent_cases_example.json`.

Không đưa `gold` hoặc nhãn đáp án vào model và retrieval tool. Ghi nguồn dữ liệu và quyền sử dụng. Cách chuyển một số định dạng Day 6: [starter/README.md](../starter/README.md).
