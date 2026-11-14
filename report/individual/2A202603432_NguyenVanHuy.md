# Báo cáo Day 7

## Dữ liệu và benchmark

- Nguồn: bài báo *RF Energy-Harvesting Techniques: Applications, Recent Developments, Challenges, and Future Opportunities*, DOI [10.3390/telecom6030045](https://doi.org/10.3390/telecom6030045), CC BY 4.0 theo manifest Day 6. Bộ dữ liệu có 288 paragraph chunks từ strategy B (`max_size=500`) và 24 câu hỏi: 17 dev (15 answerable, 2 unanswerable), 7 test (5 answerable, 2 unanswerable).
- Để tránh dùng lại các câu Day 6 đã xem, đã tạo bộ test bổ sung [day7_independent_test_questions.json](../../data/day7_independent_test_questions.json): 5 câu có đáp án và 2 câu thiếu bằng chứng, câu hỏi mới trên cùng tài liệu/corpus. `retrieval_query_en` chỉ dịch từ câu hỏi để dùng với cấu hình lexical đã chọn. Bộ này được chạy một lần sau khi chốt cấu hình; không dùng kết quả để điều chỉnh hệ thống.
- Vector store: PostgreSQL + pgvector của Day 6, strategy B. Embedding: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`.
- Agent: OpenRouter `openai/gpt-4o-mini`; đã chạy dev bằng dense/lexical và bộ test độc lập bằng lexical; top-k 3, tối đa 4 lượt search, context budget 2000 ký tự.
- Câu có đáp án dùng gold `{source_id, page, evidence}`. Retrieval hit yêu cầu cùng nguồn, cùng page và evidence gold xuất hiện nguyên văn trong chunk. Câu không đủ bằng chứng không tính vào mẫu số Hit@k.
- Thử nghiệm query: câu hỏi benchmark gốc là tiếng Việt trong khi corpus tiếng Anh. Thêm `retrieval_query_en` là bản dịch thủ công cho 17 câu dev để thử query rewriting; không đưa gold/expected answer vào query, không sửa câu hỏi gốc, gold hoặc 7 câu test Day 6. Bộ test độc lập mới có field query dịch riêng, tạo từ câu hỏi.

## Retrieval và thử nghiệm

| Cấu hình | Phương pháp, top-k, filter, rerank, context budget | Giả thuyết / thay đổi | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian / chi phí |
|---|---|---|---|---|---|---|---|
| Baseline — lexical, query Việt | TF-IDF, top-3; câu gốc | Đo từ vựng không dịch trên corpus tiếng Anh | dev | 1/15 (6,7%) | 4/15 (26,7%) | N/A — retrieval-only | median 1,16 ms/query; không dùng API |
| Dense, query Việt | Day 6 strategy B, multilingual MiniLM, top-3 | Dense baseline trên query gốc | dev | 4/15 (26,7%) | 7/15 (46,7%) | N/A — retrieval-only | median 83,80 ms/query; không dùng API |
| Hybrid, query Việt | RRF, dense + TF-IDF, candidate-k 20, RRF-k 60, top-3 | Kết hợp hai ranking gốc | dev | 4/15 (26,7%) | 7/15 (46,7%) | N/A — retrieval-only | median 103,34 ms/query; không dùng API |
| Cải thiện — lexical, query Anh | TF-IDF, top-3; `retrieval_query_en` | Giảm lệch ngôn ngữ query/corpus | dev | 9/15 (60,0%) | 12/15 (80,0%) | N/A — retrieval-only | median 1,31 ms/query; không dùng API |
| Cải thiện — dense, query Anh | Day 6 strategy B, multilingual MiniLM, top-3; `retrieval_query_en` | Kiểm tra tác động dịch lên dense | dev | 4/15 (26,7%) | 8/15 (53,3%) | N/A — retrieval-only | median 76,07 ms/query; không dùng API |
| Cải thiện — hybrid, query Anh | RRF, dense + TF-IDF, candidate-k 20, RRF-k 60, top-3; `retrieval_query_en` | Kiểm tra tác động dịch lên RRF | dev | 6/15 (40,0%) | 9/15 (60,0%) | N/A — retrieval-only | median 88,46 ms/query; không dùng API |
| Cấu hình ứng viên cho test mới | Lexical + query Anh | Tốt nhất trên dev; chưa tuyên bố tổng quát hóa | dev | 9/15 (60,0%) | 12/15 (80,0%) | N/A — retrieval-only | median 1,31 ms/query |
| Baseline — lexical, query Việt | TF-IDF, top-3; `question` | Baseline trên test độc lập | test độc lập (5 câu có đáp án) | 1/5 (20,0%) | 2/5 (40,0%) | N/A — retrieval-only | median 0,65 ms/query; không dùng API |
| Cấu hình chọn — lexical, query Anh | TF-IDF, top-3; `retrieval_query_en` | Query rewriting của cấu hình đã chọn | test độc lập (5 câu có đáp án) | 5/5 (100%) | 5/5 (100%) | N/A — retrieval-only | median 1,22 ms/query; không dùng API |

Với retrieval-only, Context Evidence Rate (CER) là N/A vì chưa có context cuối gửi model. Với agent, CER được tính trên context tích lũy ở lượt search cuối (context thực sự được gửi ở lần quyết định cuối): câu được tính khi một gold quote xuất hiện nguyên văn trong chunk có đúng `source_id` và `page` trong `context_ids`; chỉ câu answerable chạy thành công thuộc mẫu số. Đây là quy tắc exact-match bảo thủ, nhất quán với định nghĩa hit của benchmark. Retrieval chạy local, không phát sinh phí API. Kết quả raw query được lưu ở `starter/results/naming-check-all-methods/`; kết quả query Anh ở `starter/results/retrieval-query-en-dev/`. Lệnh tái lập:

```powershell
python starter/retrieval_benchmark.py --chunks data/day6_chunks.json --questions data/day6_questions.json --split dev --output starter/results/retrieval-query-en-dev --day6-root "<DAY6_ROOT>" --database-url $env:DATABASE_URL --methods lexical dense hybrid --query-field retrieval_query_en
```

Hai lỗi dev và phân tích:

1. Với query Việt, TF-IDF không có kết quả cho q02, q03, q06, q08 và q09 do không có token giao với corpus tiếng Anh. Dịch query cải thiện mạnh lexical; Evidence Hit@3 tăng từ 4/15 lên 12/15. Đây là giả thuyết chính được xác nhận trên dev.
2. q10 vẫn không tìm thấy evidence chứa khoảng số cụ thể `0.1–10 μW/cm²` trong top-3 của cả ba phương pháp sau dịch; kết quả chủ yếu nói chung về khác biệt đô thị/nông thôn. Với q02, dense query Anh tìm gold ở rank 2 nhưng hybrid đưa nó khỏi top-3, cho thấy RRF hiện tại có thể làm giảm thứ hạng khi hai retriever bất đồng. Cần thử query cụ thể hơn và rerank candidates trên dev trước khi chốt.

Lexical + query Anh được chọn theo dev rồi đánh giá một lần trên bộ test độc lập bổ sung. Kết quả test và giới hạn mẫu nhỏ được báo riêng, không dùng để điều chỉnh cấu hình.

## Agent và đánh giá

- Tool: `search_chunks`, tối đa 4 lượt, top-k 3; ngưỡng context 2000 ký tự; verifier model kiểm tra citation. Số lượt gọi thay đổi theo truy vấn và run; trace từng lượt lưu query, context, citation, thời gian và lỗi.

| Cấu hình / split | Tool use | Số lượt gọi | Context Evidence Rate | Grounded answer 0/1/2 và trung bình | Citation hợp lệ | Câu có citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|
| OpenRouter `openai/gpt-4o-mini` + dense / dev | 17/17 | 1/câu | 7/15 (46,7%) | 3 / 3 / 9; trung bình 1,4/2 trên 15 câu có đáp án | 20/21 | 12/12 | 2/2 | 3/15 |
| OpenRouter `openai/gpt-4o-mini` + lexical / dev | 17/17 | 20 tổng (16 câu × 1, q22 × 4) | 10/15 (66,7%) | 1 / 2 / 12; trung bình 1,73/2 trên 15 câu có đáp án | 25/25 | 14/14 | 2/2 | 1/15 |
| OpenRouter `openai/gpt-4o-mini` + lexical / dev, rerun 2026-11-14 | 17/17 | 23 tổng | 10/15 (66,7%) | 1 / 2 / 12; trung bình 1,73/2 trên 15 câu có đáp án | 23/24 | 14/14 | 2/2 | 1/15 |
| OpenRouter `openai/gpt-4o-mini` + lexical / test độc lập | 7/7 | 7 tổng (1/câu) | 5/5 (100%) | 0 / 0 / 5; trung bình 2,0/2 trên 5 câu có đáp án | 8/8 | 5/5 | 2/2 | 0/5 |

CER misses: dense q01/q04/q05/q06/q10/q12/q14/q15; lexical (cả hai lượt) q02/q05/q06/q08/q10. Các file `metrics.json` trong từng thư mục run lưu cả CER theo từng câu; `agent_metrics.py` tái lập phép tính.

Đánh giá test độc lập được giữ nguyên sau khi chọn cấu hình: lexical baseline dùng câu Việt đạt Hit@1 1/5, Evidence Hit@3 2/5; lexical + query Anh đạt 5/5 cho cả hai. Agent OpenRouter trả lời đúng/đủ 5/5 câu có đáp án, citation hỗ trợ 8/8, CER 5/5; từ chối đúng 2/2 câu thiếu evidence. Có 7/7 câu gọi search một lần, không có provider error. Median agent latency 6,77 giây/câu; retrieval latency 0,65 ms/query (baseline) và 1,22 ms/query (đã chọn). Endpoint không báo chi phí API.

| Query ID | Nhãn thủ công | Kết quả / lý do |
|---|---|---|
| indtest-01 | Answerable, grade 2; citation hợp lệ | Nêu đúng MPPT điều chỉnh điện trở tải chỉnh lưu. |
| indtest-02 | Answerable, grade 2; citation hợp lệ | Nêu đủ đèn, Wi-Fi, CCTV, giám sát môi trường và an toàn công cộng. |
| indtest-03 | Answerable, grade 2; 3/3 citation hỗ trợ | Đủ ba loại thông tin được hỏi; citation hỗ trợ cả nội dung bổ sung về cảm biến. |
| indtest-04 | Answerable, grade 2; 2/2 citation hỗ trợ | Nêu bảo trì dự đoán và nhà máy thông minh; citation hỗ trợ nội dung bổ sung. |
| indtest-05 | Answerable, grade 2; citation hợp lệ | Nêu học cộng tác, không tập trung, bảo vệ quyền riêng tư. |
| indtest-06 | Unanswerable, abstention đúng | Corpus không cho biết hãng hoặc mã sản phẩm của cột thông minh Seoul. |
| indtest-07 | Unanswerable, abstention đúng | Corpus không nêu số thiết bị IoT cụ thể trong hệ thống neural-network. |

Trace retrieval baseline ở `starter/results/independent-test-retrieval-baseline-lexical/`; trace cấu hình đã chọn ở `starter/results/independent-test-retrieval-selected-lexical-en/`. Trace, context, citation, nhãn, metrics và summary agent ở `starter/results/independent-test-agent-openrouter-lexical-en/`. Hai retrieval run không gọi model; agent endpoint không cung cấp chi phí.

| Query ID | Loại câu | Tool call và kết quả | Câu trả lời và citation | Nhãn, lý do |
|---|---|---|---|---|
| q04, q14, q15 | Có đáp án | Dense; query dịch sang Anh nhưng evidence không vào context top-3 | Agent từ chối; retry lexical với query Anh trả lời đúng cả 3 và verifier chấp nhận citation | False abstention dense; thử nghiệm retry chỉ gồm 3 câu |
| q10 | Có đáp án | Dense top-3 có ngữ cảnh RF đô thị/nông thôn nhưng thiếu khoảng số gold | Có câu trả lời nhưng 1/2 citation không hỗ trợ đủ khẳng định | Grounded answer 1/2; citation audit thủ công |
| q21, q22 | Thiếu evidence | Search trong corpus rồi abstain | Không đưa ra khẳng định/citation | Abstention đúng 2/2 |
| q09 | Có đáp án | Lexical trả đúng gold chunk ở rank 1 | Verifier từ chối vì citation set còn chứa một chunk không hỗ trợ câu trả lời; agent abstain | False abstention do chọn citation thừa, không phải retrieval miss |

- Dense agent: trace/nhãn/tổng hợp tại `starter/results/agent-openrouter-dense-dev-context-2000/`; median khoảng 4,71 giây/câu. Lexical agent: `starter/results/agent-openrouter-lexical-dev-context-2000/`; nhãn thủ công và tổng hợp metric ở `reviews.json` và `metrics.json`, median khoảng 4,89 giây/câu. Endpoint không báo chi phí cho cả hai lượt.
- Trace query Anh/retrieval lưu ở `starter/results/retrieval-query-en-dev/`; query gốc được giữ riêng trong trace. Dịch query tăng lexical retrieval mạnh nhưng cải thiện dense ít (Evidence Hit@3 +1 câu) và hybrid vừa phải (+2 câu so với raw). Lexical agent cải thiện grounded-answer mean từ 1,4 lên 1,73/2 và giảm false abstention từ 3/15 xuống 1/15 trên dev. Benchmark nhỏ, exact page/quote matching nghiêm ngặt; kết quả agent này chưa phải đánh giá test độc lập.
- Sau lần lexical agent, controller được cập nhật để bắt buộc mỗi phản hồi dùng tool và yêu cầu chỉ trích dẫn các chunk tối thiểu, trực tiếp hỗ trợ câu trả lời. Thử riêng q09 bằng Gemini `gemini-3.5-flash` + lexical, context budget 2000: agent search một lần, trả lời có citation `telecom-06-00045:11:paragraph:1:a8cab621d251`, verifier chấp nhận. Đây là smoke test một câu, không gộp vào metrics dev của OpenRouter; trace và summary tại `starter/results/agent-gemini-lexical-q09/`.
- Khi chạy đủ 17 câu dev với Gemini, endpoint trả HTTP 429 (Too Many Requests); runner dừng và không ghi metrics/partial dev output. Không tính lượt lỗi vào chất lượng. Controller dùng `tool_choice=auto` cho Gemini, thử lại một lần nếu Gemini không phát tool call, và chấp nhận JSON verifier trong code fence. Test suite sau thay đổi: 39 tests pass. Chi phí dịch vụ không được endpoint báo.
- Ngày 2026-11-14, chạy lại toàn bộ dev bằng OpenRouter `openai/gpt-4o-mini` sau khi nạp cấu hình mới từ `.env`: endpoint tiếp tục trả HTTP 402 (Payment Required) ở request đầu tiên. Runner dừng, không có trace hoặc metrics mới; không tính lượt lỗi vào chất lượng.
- Sau khi cập nhật key lần nữa, chạy thành công lại toàn bộ 17 câu dev bằng OpenRouter `openai/gpt-4o-mini`, lexical top-3, tối đa 4 lượt search, context budget 2000. Có 14 câu được trả lời và 3 câu abstain; tổng 23 lượt search, median 8,91 giây/câu; endpoint không báo chi phí. Chấm thủ công: grounded answer 1/2/12 (điểm 0/1/2), trung bình 1,73/2 trên 15 câu có đáp án; citation hỗ trợ 23/24, 14/14 câu trả lời có citation; abstention đúng 2/2, từ chối nhầm 1/15. q02 abstain nhầm do top-3 tìm không đúng evidence; q05 và q10 trả lời một phần, lần lượt thiếu một số yếu tố và khoảng số; citation thứ hai của q08 không hỗ trợ câu trả lời. Nhãn cùng lý do ở `starter/results/agent-openrouter-lexical-dev-context-2000-rerun-20261114-2037/reviews.json`, metrics ở `metrics.json`, trace và summary trong cùng thư mục.

## Thử thách nâng cao (nếu thực hiện)

- Tài liệu, nguồn, quyền sử dụng, số trang và phiên bản:
- Cách xử lý text, bảng, ảnh, biểu đồ; phạm vi index và phần chưa xử lý:
- Cách chia benchmark, schema evidence, model và cấu hình đã chốt trên dev:

| Nhóm test | Đạt / tổng | Tỷ lệ | Lỗi / nhận xét |
|---|---|---|---|
| Bảng | | | |
| Ảnh, sơ đồ | | | |
| Biểu đồ | | | |
| Multi-hop | | | |
| Text | | | |
| Thiếu bằng chứng | | | |
| **Toàn bộ** | | | |

- Trace, nhãn và evidence từng câu; thời gian, chi phí, lỗi hệ thống:
- Giới hạn, cách tái lập và đường dẫn benchmark:
