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

## Corpus Thử thách nâng cao (local)

- Nguồn: OpenStax, *Business Law I Essentials 2e*, ©2026 Rice University; sách được phát triển bởi Barnes & Noble Education LoudCloud. Xem [trang sách chính thức](https://openstax.org/details/books/business-law-i-essentials-2e). Nội dung sách theo CC BY-NC-SA 4.0: chỉ sử dụng/chia sẻ phi thương mại, ghi công và phát hành bản phái sinh theo cùng giấy phép. Mỗi hình có thể có giấy phép/ghi công riêng trong caption; phải giữ và kiểm tra các điều khoản đó. Khi phân phối lại nội dung sách, tuân thủ yêu cầu attribution “Access for free at openstax.org” trong bản số/trang in tương ứng.
- Bản PDF cục bộ `bonus.pdf` có 164 trang vật lý. `bonus_chunks.json` có 534 chunks trên các trang PDF 11–154 (144 trang vật lý; trang in trong sách thường thấp hơn số trang PDF 10 trang). Các trang 1–10 là bìa/front matter; trang 155–160 là Answer Key và bị loại để tránh rò rỉ đáp án; trang 161–164 là Index và bị loại vì chỉ phục vụ điều hướng. Cần ghi số trang PDF trong citation, không nhầm với số trang in.
- Chunk builder trích xuất text, tạo 17 biểu diễn bảng có cấu trúc và thêm mô tả thủ công cho 7 hình/biểu đồ/sơ đồ; 69 ảnh được trích xuất để kiểm tra. Đây chưa phải kiểm kê thị giác đầy đủ: nhiều ảnh chỉ có caption/text chunk, chưa có mô tả riêng; các hình được dùng trong benchmark phải được đối chiếu trực quan với ảnh gốc và caption.
- [`bonus_questions.json`](bonus_questions.json) được tạo từ `starter/build_bonus_questions.py`: 18 dev (15 có đáp án, 3 thiếu bằng chứng) và 30 test (24 có đáp án, 6 thiếu bằng chứng). Test có 6 Bảng, 5 Ảnh/sơ đồ, 5 Biểu đồ, 4 Multi-hop, 4 Text và 6 Thiếu bằng chứng. Trong benchmark bonus, mọi phần tử `gold` là evidence bắt buộc, trừ khi câu hỏi khai báo `evidence_groups` với `min_matches` và `gold_indices` cho lựa chọn thay thế (ví dụ cần hai trong bốn quốc gia). CER yêu cầu đủ mọi nhóm evidence trong context cuối, cùng `source_id`/trang và quote nguyên văn.
- Các file `bonus.pdf`, `bonus_chunks.json`, `bonus_questions.json` và `bonus_figures/` bị loại khỏi Git theo mặc định. Không phân phối chúng công khai nếu chưa kiểm tra giấy phép phi thương mại, attribution/share-alike của văn bản và điều khoản riêng của từng hình. Có thể tái tạo cục bộ bằng cách lấy PDF từ trang OpenStax ở trên rồi chạy:

```powershell
python starter\build_bonus_chunks.py
python starter\build_bonus_questions.py
```

Chạy agent trên dev/test và tổng hợp nhãn thủ công:

```powershell
python starter\run_bonus_agent.py --chunks data\bonus_chunks.json --questions data\bonus_questions.json --split dev --output starter\results\bonus-agent-dev
python starter\bonus_metrics.py --chunks data\bonus_chunks.json --questions data\bonus_questions.json --traces starter\results\bonus-agent-test\traces.json --reviews starter\results\bonus-agent-test\manual_reviews.json --split test --output starter\results\bonus-agent-test\audit-summary.json
```

`run_bonus_agent.py` chỉ tạo trace và kiểm tra evidence tự động; nó không chấm độ đúng/đủ câu trả lời hay độ an toàn của abstention. `bonus_metrics.py` chỉ báo pass rate khi có một nhãn cho từng câu và kiểm tra đủ evidence/citation; lỗi và kết quả thiếu vẫn thuộc mẫu số. Lượt `bonus-agent-test` hiện có là exploratory, được chạy trước thay đổi controller và đã được xem; không dùng làm test độc lập cuối hoặc để khẳng định đạt ngưỡng 90%. Nếu đã xem kết quả để chỉnh pipeline, phải tạo một test mới trước khi kết luận.
