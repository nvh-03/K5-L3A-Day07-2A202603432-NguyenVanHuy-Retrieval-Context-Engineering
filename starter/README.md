# Starter Day 7

| File | Công dụng |
|---|---|
| `agentic.py` | Agent loop, OpenAI-compatible controller dùng tool calling, context packing và citation verifier |
| `baseline.py` | TF-IDF lexical baseline, chạy offline |
| `retrieval.py` | Lexical, dense adapter Day 6 và hybrid RRF |
| `retrieval_benchmark.py` | So sánh retrieval, xuất metrics và trace cho mỗi query |
| `run_agent.py` | Chạy agent với model thật trên dev hoặc test |
| `convert_day6.py` | Chuyển một số trường JSON từ Day 6 |
| `agent_metrics.py` | Tổng hợp nhãn đánh giá do bạn tự chấm |

Starter có adapter và controller mẫu; bạn cần cấu hình model/vector store thật, kiểm tra corpus và tự audit chất lượng. Mock chỉ dùng để test code, không dùng báo cáo benchmark.

## 1. Kết nối agent

Trong `agentic.py`:

- `OpenAICompatibleController.decide` gọi Chat Completions với các tool `search_chunks`, `submit_answer` và `abstain`; model quyết định tìm tiếp, trả lời hay từ chối.
- `DenseRetriever` gọi embedder và `PgVectorStore` của Day 6. Có thể thay bằng lexical hoặc hybrid đã triển khai trong `retrieval.py`.
- `run_agent` gom retrieval results, giữ context trong giới hạn ký tự, bắt buộc citation ID có trong context và câu trả lời. Controller thật gọi verifier model thứ hai; khi verifier không xác nhận mọi citation, agent từ chối.

`OpenAICompatibleController.from_env()` đọc `OPENAI_MODEL`, `OPENAI_API_KEY` và tùy chọn `OPENAI_BASE_URL` (mặc định OpenAI API). Với DeepSeek, đặt `OPENAI_MODEL=deepseek-chat`, `OPENAI_BASE_URL=https://api.deepseek.com` và `DEEPSEEK_API_KEY`. Với OpenRouter, đặt `OPENAI_BASE_URL=https://openrouter.ai/api/v1`, `OPENROUTER_MODEL=openai/gpt-4o-mini` và `OPENROUTER_API_KEY`. Với Gemini, dùng endpoint `https://generativelanguage.googleapis.com/v1beta/openai/`, đặt `GEMINI_MODEL` và `GEMINI_API_KEY`; Gemini dùng `tool_choice=auto` theo OpenAI compatibility API. Copy `.env.example` thành `.env` ở thư mục gốc repo, điền cấu hình vào file local; runner tự nạp `.env`, còn `.gitignore` loại file này khỏi Git:

```powershell
Copy-Item .env.example .env
# Sửa .env bằng VS Code hoặc editor của bạn
python starter/run_agent.py --chunks data/day6_chunks.json --questions data/day6_questions.json --split dev --output starter/results/agent-dev --method lexical
```

Không ghi key vào code hoặc commit `.env`. Câu hỏi và context được gửi tới endpoint đã cấu hình; chỉ dùng dữ liệu được phép chia sẻ với provider đó. Verifier model giảm rủi ro citation không hỗ trợ nhưng không thay thế việc người làm bài đọc đối chiếu thủ công. Lỗi API/retriever được báo rõ, không chuyển sang mock.

Để chạy agent với dense hoặc hybrid, thêm `--method dense` hoặc `--method hybrid` và `--day6-root "<đường-dẫn-repo-Day-6>"`; PostgreSQL Day 6 phải có strategy B và cần cấu hình model/embedding như phần retrieval phía trên. `--max-searches`, `--top-k` và `--budget` cho phép đổi giới hạn lượt tìm, số kết quả và ngân sách context. Mặc định context 800 ký tự; chunk dài sẽ được cắt, và verifier chỉ thấy phần thực sự gửi model.

## 2. Chạy TF-IDF baseline

Chạy từ thư mục gốc với Python 3.11 trở lên:

```bash
python3 -m unittest discover -s tests -v
python3 starter/baseline.py --chunks data/example_chunks.json --questions data/example_questions.json --split dev --output starter/results/example-dev
```

Kết quả có `summary.json` và `traces.json`. Dữ liệu mẫu chỉ có một câu, không đủ để nộp bài. TF-IDF là lexical retrieval, không dùng filter và không thay dense retrieval.

## 3. Dùng dữ liệu Day 6

Dữ liệu Day 6 đã chuyển schema có sẵn tại `data/day6_chunks.json` và `data/day6_questions.json`. Chunks được tái tạo bằng paragraph chunker strategy B từ PDF gốc trong repo Day 6; benchmark gồm câu hỏi Day 6 và bốn câu thiếu bằng chứng bổ sung. Nguồn, license và điều chỉnh evidence được ghi trong [`data/README.md`](../data/README.md).

Chạy baseline trên dev:

```bash
python starter/baseline.py --chunks data/day6_chunks.json --questions data/day6_questions.json --split dev --output starter/results/day6-export-dev
```

## 4. So sánh retrieval

`retrieval.py` cung cấp ba phương pháp: TF-IDF lexical, dense adapter gọi `PgVectorStore` và query embedder của Day 6, cùng hybrid RRF kết hợp hai ranking. Chạy trên cùng corpus và split dev:

```bash
python starter/retrieval_benchmark.py --chunks data/day6_chunks.json --questions data/day6_questions.json --split dev --output starter/results/retrieval-dev --day6-root "<đường-dẫn-repo-Day-6>" --methods lexical dense hybrid
```

Dense/hybrid cần PostgreSQL Day 6 đã có strategy B, `.env` với `DATABASE_URL`, và dependencies của Day 6 đã cài. Mặc định model và revision được lấy từ cấu hình Day 6; nếu index dùng model khác, truyền `--embedding-model` và `--embedding-revision` tương ứng. Filter Day 6 hiện hỗ trợ `section`.

Để thử dịch truy vấn tiếng Việt sang tiếng Anh mà vẫn giữ câu hỏi gốc và gold, chạy thêm `--query-field retrieval_query_en` trên dev và lưu vào thư mục kết quả riêng:

```bash
python starter/retrieval_benchmark.py --chunks data/day6_chunks.json --questions data/day6_questions.json --split dev --output starter/results/retrieval-query-en-dev --day6-root "<đường-dẫn-repo-Day-6>" --methods lexical dense hybrid --query-field retrieval_query_en
```

Trace giữ cả `question` gốc, `query` thực sự dùng để tìm và `query_field`; summary cũng ghi trường truy vấn để kết quả có thể tái lập. Truy vấn tiếng Anh chỉ được thêm cho câu dev, không thay đổi test hay gold.

Mỗi phương pháp tạo hai file riêng có tên ghi rõ split và phương pháp, ví dụ `dev-lexical-summary.json`, `dev-lexical-traces.json`, `dev-dense-summary.json`, `dev-dense-traces.json`, `dev-hybrid-summary.json` và `dev-hybrid-traces.json`. Summary ghi Hit@1, Evidence Hit@3 (`n/N`, tỷ lệ), thời gian và cấu hình; trace lưu query, filter, kết quả có rank/score/ID/source/page và nhãn evidence hit. Hybrid ghi thêm score/rank của dense và lexical. Các câu thiếu bằng chứng vẫn có trace nhưng không nằm trong mẫu số retrieval metrics. Chạy thử offline chỉ lexical bằng `--methods lexical`; lỗi kết nối dense được báo, không chuyển ngầm sang kết quả giả.

Nếu dùng output Day 6 khác, xuất chunk và câu hỏi thành hai JSON array. Starter Day 6 không quy định tên bảng hay cách xuất; bạn cần tự thực hiện. Nếu chunk có `chunk_id`, `document_id`, `source`, `page`, `text`, `metadata` và câu hỏi có `gold_source_id`, `gold_page`, `evidence_quote`, chạy:

```bash
python3 starter/convert_day6.py --chunks <day6_chunks.json> --questions <day6_questions.json> --output starter/data/converted
python3 starter/baseline.py --chunks starter/data/converted/chunks.json --questions starter/data/converted/questions.json --split dev --output starter/results/dev-tfidf
```

Thay phần trong `< >` bằng đường dẫn thật. Script chỉ đổi tên trường, không tự truy cập database hay đoán evidence. Nếu cấu trúc khác, tự viết adapter. Đối chiếu lại nguồn, trang và evidence.

`--split dev` chỉ chấm dev. Sau khi chốt cấu hình, dùng `--split test` và chọn thư mục kết quả khác. Nếu test Day 6 từng dùng để chỉnh hệ thống, tạo test mới theo [GUIDE.md](../GUIDE.md). Baseline mẫu dùng evidence nằm trong một chunk và context từ top-3; cần mở rộng hoặc tự đánh giá nếu dùng multi-hop, context từ nhiều lượt hay schema khác. Khớp nguyên văn bằng code không thay thế đánh giá thủ công.

## 5. Tổng hợp đánh giá agent

Sau khi chạy agent thật và tự chấm, chuẩn bị ba JSON array:

- `cases.json`: mỗi câu có `id`, `split`, `answerable` (`true` nếu có đủ evidence); câu answerable cần `gold` để tính CER.
- `traces.json`: mỗi kết quả có `query_id`, `status` (`answered`, `abstain`, `error`), `events`, `citations`. Thêm `query_id` vào kết quả `run_agent`; lỗi kết nối ghi riêng với `status: "error"`. Script đếm tool use qua event `search`: nếu dùng nhiều tool, chuẩn hóa mỗi lượt retrieval về event này và ghi tên tool trong trường khác, hoặc tự viết metric tương đương.
- `reviews.json`: mỗi nhãn có `query_id`, `citation_support` là danh sách đúng/sai ứng với từng citation. Câu có đáp án cần `answer_grade` 0–2 theo [BENCHMARK.md](../BENCHMARK.md); nếu bị từ chối, chấm 0. Câu thiếu evidence cần `abstention_correct` (`true`/`false`) do người chấm xác nhận. Lần chạy lỗi không cần nhãn.
- `agent_metrics.py` cũng tính `context_evidence` trên context của lượt search cuối (context tích lũy thực sự được gửi ở lần quyết định cuối): một câu được tính khi một gold quote xuất hiện nguyên văn trong chunk đúng `source_id` và `page` thuộc `context_ids`. Câu lỗi provider và câu không answerable không thuộc mẫu số CER.

```bash
python3 starter/agent_metrics.py --cases <cases.json> --traces <traces.json> --reviews <reviews.json> --split test --output starter/results/agent-test/summary.json
```

Thay đường dẫn trong `< >`. Script tổng hợp nhãn bạn đã chấm, không tự đánh giá nội dung. Mẫu số bằng 0 nghĩa là không áp dụng. Lỗi kết nối được báo riêng, không tính vào chất lượng; giữ trace và nhãn để đối chiếu.

## Lưu ý

TF-IDF dùng cách tách từ đơn giản. `baseline.py` dùng mặc định context budget 800 ký tự, gồm cả nguồn; chunk không vừa bị bỏ. Bạn có thể chọn cách khác. File kết quả cùng tên sẽ bị ghi đè. `starter/data/` và `starter/results/` không được Git theo dõi mặc định; nếu được phép chia sẻ, dùng `git add -f <đường-dẫn>`, hoặc ghi cách tái tạo. Không nộp dữ liệu mật và secret.

Khung agent ưu tiên giữ chunk từ lần search trước. Khi chunk đầu chiếm gần hết budget, lần search sau có thể không thêm được evidence; hãy kiểm tra trace và thử cách chọn context phù hợp trên dev. Citation ID hợp lệ hoặc verifier trả “đúng” không đảm bảo câu trả lời được hỗ trợ; cần chấm thủ công.

## 6. Thử thách nâng cao

Corpus, giấy phép, phạm vi trang, giới hạn mô tả ảnh và cách tái tạo được ghi trong [`data/README.md`](../data/README.md). Các file PDF/chunks/ảnh bonus ở thư mục gốc bị loại khỏi Git theo mặc định; kiểm tra CC BY-NC-SA 4.0 và attribution riêng của ảnh trước khi phân phối.

Tạo corpus và benchmark cục bộ từ PDF OpenStax đã tải hợp lệ:

```powershell
python starter\build_bonus_chunks.py
python starter\build_bonus_questions.py
```

Chạy agent trên dev để thử cấu hình. Sau khi chốt cấu hình, chỉ chạy một test chưa được dùng để chỉnh:

```powershell
python starter\run_bonus_agent.py --split dev --output starter\results\bonus-agent-dev
python starter\run_bonus_agent.py --split test --output starter\results\bonus-agent-test
```

Agent runner lưu `traces.json`, context cuối và `automatic_checks.json`; các kiểm tra tự động chỉ xác nhận evidence có trong context/citation, không tự gán nhãn đúng/sai. Chấm thủ công từng câu trong `manual_reviews.json`, gồm `answer_grade` (0–2) và một `citation_support` boolean cho mỗi citation; câu thiếu evidence cần `abstention_correct`. Với câu nhiều evidence, mặc định mọi phần tử `gold` đều bắt buộc. `evidence_groups` chỉ rõ nhóm lựa chọn và số evidence tối thiểu cần thiết.

Tính điểm, CER đầy đủ theo nhóm evidence, breakdown, lỗi và độ trễ bằng:

```powershell
python starter\bonus_metrics.py --chunks data\bonus_chunks.json --questions data\bonus_questions.json --traces starter\results\bonus-agent-test\traces.json --reviews starter\results\bonus-agent-test\manual_reviews.json --split test --output starter\results\bonus-agent-test\summary.json
```

Pass rate dùng toàn bộ câu test làm mẫu số; lỗi và câu không có trace đều thất bại. CER chỉ tính câu answerable chạy thành công và chỉ đạt khi context cuối chứa đủ evidence bắt buộc với quote nguyên văn, đúng nguồn/trang. Chi phí chỉ được cộng khi trace có `cost_usd`; nếu provider không trả usage/cost thì metrics báo `null`, không coi là 0. Test bonus hiện có đã được xem và là exploratory; phải tạo test độc lập mới sau khi chỉnh controller trước khi báo kết quả đủ điều kiện.
