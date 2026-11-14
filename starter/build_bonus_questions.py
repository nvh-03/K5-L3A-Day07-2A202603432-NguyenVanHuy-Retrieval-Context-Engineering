"""Build dev and test benchmark questions for bonus.pdf with strict schema validation."""
import json
from pathlib import Path
from baseline import validate

SOURCE_ID = 'bonus-business-law-2e'

DEV_QUESTIONS = [
    # Bảng (3)
    {
        "id": "bonus-dev-01",
        "split": "dev",
        "category": "Bảng",
        "question": "Theo Bảng 4.1, ví dụ nào được nêu cho thẩm quyền của Quốc hội khi điều chỉnh các công cụ (instrumentalities) của thương mại giữa các bang?",
        "retrieval_query_en": "Table 4.1 instrumentalities of interstate commerce Congress regulation equipment manufacturing plants",
        "answerable": True,
        "expected_answer": "Quốc hội có thể thông qua các quy định bắt buộc áp dụng một số tiêu chuẩn an toàn nhất định cho thiết bị được sử dụng trong các nhà máy sản xuất.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 50,
                "evidence": "Congress could pass regulations mandating certain safety standards for equipment used in manufacturing plants."
            }
        ]
    },
    {
        "id": "bonus-dev-02",
        "split": "dev",
        "category": "Bảng",
        "question": "Theo Bảng 8.2 về các điều khoản để ngỏ theo UCC, nếu địa điểm giao hàng không được nêu thì quy định mặc định là gì và theo điều khoản UCC nào?",
        "retrieval_query_en": "Table 8.2 UCC open term delivery default provision seller's place of business UCC 2-308(a)",
        "answerable": True,
        "expected_answer": "Nếu địa điểm giao hàng không được nêu, mặc định là địa điểm kinh doanh của người bán (seller's place of business) theo điều khoản UCC 2-308(a).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 89,
                "evidence": "| Delivery | If delivery is not named, default is \"seller's place of business.\" | UCC 2-308(a) |"
            }
        ]
    },
    {
        "id": "bonus-dev-03",
        "split": "dev",
        "category": "Bảng",
        "question": "Trong Bảng 9.5 về các biện pháp bào chữa trước cáo buộc theo Title VII, ba biện pháp bào chữa được liệt kê là gì?",
        "retrieval_query_en": "Table 9.5 Defenses to Title VII Claims BFOQ Merit Defense Seniority System",
        "answerable": True,
        "expected_answer": "Ba biện pháp bào chữa là: The Bona Fide Occupational Qualification Defense (BFOQ), The Merit Defense, và The Seniority Defense System.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 107,
                "evidence": "The Bona Fide Occupational Qualification Defense (BFOQ)"
            },
            {
                "source_id": SOURCE_ID,
                "page": 107,
                "evidence": "The Merit Defense"
            },
            {
                "source_id": SOURCE_ID,
                "page": 107,
                "evidence": "The Seniority Defense System"
            }
        ]
    },

    # Ảnh, sơ đồ (3)
    {
        "id": "bonus-dev-04",
        "split": "dev",
        "category": "Ảnh, sơ đồ",
        "question": "Trong sơ đồ Hình 13.3 về các nguồn của luật quốc tế, ba thành phần nào được thể hiện dưới dạng các bánh răng lồng vào nhau?",
        "retrieval_query_en": "Figure 13.3 interlocking gears treaties customs organizations sources of international law",
        "answerable": True,
        "expected_answer": "Ba thành phần là điều ước quốc tế (treaties), tập quán quốc tế (customs), và các tổ chức quốc tế (organizations).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 137,
                "evidence": "1. Top gear: 'treaties'\n2. Lower-left gear: 'customs'\n3. Lower-right gear: 'organizations'"
            }
        ]
    },
    {
        "id": "bonus-dev-05",
        "split": "dev",
        "category": "Ảnh, sơ đồ",
        "question": "Trong bức ảnh Hình 6.7 chụp người dùng cưa máy khi đi chân trần, khái niệm pháp lý nào trong luật bồi thường thiệt hại ngoài hợp đồng (tort) được minh họa?",
        "retrieval_query_en": "Figure 6.7 chainsaw bare feet comparative negligence plaintiff risk",
        "answerable": True,
        "expected_answer": "Bức ảnh minh họa khái niệm lỗi hỗn hợp / bất cẩn so sánh (comparative negligence) của nguyên đơn khi tự đặt mình vào rủi ro nguy hiểm.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 74,
                "evidence": "he could be responsible for comparative negligence."
            }
        ]
    },
    {
        "id": "bonus-dev-06",
        "split": "dev",
        "category": "Ảnh, sơ đồ",
        "question": "Theo chú thích Hình 6.4, nếu ngựa thoát ra khỏi khu vực có hàng rào và gây thiệt hại, chủ sở hữu phải chịu trách nhiệm như thế nào?",
        "retrieval_query_en": "Figure 6.4 horses get out of a fenced-in area owner liable damage loose",
        "answerable": True,
        "expected_answer": "Chủ sở hữu phải chịu trách nhiệm đối với bất kỳ thiệt hại nào do chúng gây ra trong khi xổng ra ngoài.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 71,
                "evidence": "If horses get out of a fenced-in area, the owner would be liable for any damage they cause while loose."
            }
        ]
    },

    # Biểu đồ (3)
    {
        "id": "bonus-dev-07",
        "split": "dev",
        "category": "Biểu đồ",
        "question": "Trên biểu đồ phong cách đàm phán Hình 2.3, phong cách nào tương ứng với mức quan tâm cao đến bản thân (High Concern for Self) và quan tâm cao đến đối phương (High Concern for Others)?",
        "retrieval_query_en": "Figure 2.3 negotiating styles chart High Concern for Self High Concern for Others Collaborating",
        "answerable": True,
        "expected_answer": "Phong cách hợp tác (Collaborating).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 25,
                "evidence": "- Top-Right quadrant: 'Collaborating' style (High Concern for Self, High Concern for Others)."
            }
        ]
    },
    {
        "id": "bonus-dev-08",
        "split": "dev",
        "category": "Biểu đồ",
        "question": "Trong biểu đồ Hình 2.3, hai trục tọa độ ngang và dọc thể hiện những đại lượng nào?",
        "retrieval_query_en": "Figure 2.3 chart axes Horizontal Axis Concern for Self Vertical Axis Concern for Others",
        "answerable": True,
        "expected_answer": "Trục ngang (X) thể hiện 'Concern for Self' (Mức độ quan tâm đến bản thân) từ Low đến High; trục dọc (Y) thể hiện 'Concern for Others' (Mức độ quan tâm đến đối phương) từ Low đến High.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 25,
                "evidence": "- Horizontal Axis (X-axis): 'Concern for Self', ranging from Low (left) to High (right).\n- Vertical Axis (Y-axis): 'Concern for Others', ranging from Low (bottom) to High (top)."
            }
        ]
    },
    {
        "id": "bonus-dev-09",
        "split": "dev",
        "category": "Biểu đồ",
        "question": "Theo lưu đồ kiểm tra thương mại 4 bước trong Hình 4.3 (Central Hudson test), câu hỏi đầu tiên ở Bước 1 là gì?",
        "retrieval_query_en": "Figure 4.3 four-part test Step 1 commercial speech illegal activity misleading",
        "answerable": True,
        "expected_answer": "Bước 1 đặt câu hỏi: 'Does the speech concern an illegal activity? Is it misleading?' (Phát ngôn có liên quan đến hoạt động bất hợp pháp hoặc gây hiểu lầm hay không?).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 53,
                "evidence": "Step 1 (Diamond): 'Does the speech concern an illegal activity? Is it misleading?'"
            }
        ]
    },

    # Multi-hop (3)
    {
        "id": "bonus-dev-10",
        "split": "dev",
        "category": "Multi-hop",
        "question": "Theo Bảng 4.2 tóm tắt Tuyên ngôn Nhân quyền, tu chính án nào bảo vệ công dân khỏi việc khám xét và thu giữ phi lý (trang 51), và tu chính án nào quy định quyền có phiên xét xử công khai, nhanh chóng và có luật sư (trang 52)?",
        "retrieval_query_en": "Table 4.2 Bill of Rights unwarranted search and seizure expeditious public trial attorney Sixth Fourth",
        "answerable": True,
        "expected_answer": "Tu chính án thứ Tư (Fourth Amendment) bảo vệ khỏi việc khám xét và thu giữ phi lý; Tu chính án thứ Sáu (Sixth Amendment) bảo đảm quyền được xét xử công khai, nhanh chóng và có luật sư.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 51,
                "evidence": "| Fourth | States that government can only issue warrants with probable cause and protects U.S. citizens from unwarranted search and seizure. |"
            },
            {
                "source_id": SOURCE_ID,
                "page": 52,
                "evidence": "| Sixth | Provides citizens with the right to an expeditious public trial, the right to an attorney, and the right to an impartial jury. |"
            }
        ]
    },
    {
        "id": "bonus-dev-11",
        "split": "dev",
        "category": "Multi-hop",
        "question": "Theo định nghĩa tại Mục 2-105 của UCC (trang 88), hai đặc điểm chính của hàng hóa (goods) là gì, và trong Bảng 8.2 (trang 89), điều khoản mặc định là gì nếu giá không được nêu?",
        "retrieval_query_en": "UCC Section 2-105 features of goods movable tangible Table 8.2 default price reasonable price",
        "answerable": True,
        "expected_answer": "Hàng hóa phải có đặc điểm là có thể di dời (movable) và hữu hình (tangible); nếu giá không được nêu thì điều khoản mặc định theo Bảng 8.2 là giá hợp lý (reasonable price) căn cứ UCC 2-305(1).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 88,
                "evidence": "primary features of goods are that they are movable and tangible."
            },
            {
                "source_id": SOURCE_ID,
                "page": 89,
                "evidence": "| Price | If price is not named, the default is \"reasonable price.\" | UCC 2-305(1) |"
            }
        ]
    },
    {
        "id": "bonus-dev-12",
        "split": "dev",
        "category": "Multi-hop",
        "question": "Tính đến tháng 1 năm 2018, có bao nhiêu quốc gia đã thông qua CISG (trang 140), và theo Bảng 13.1 (trang 141), Hoa Kỳ thuộc hệ thống Thông luật (Common Law) hay Dân luật (Civil Law)?",
        "retrieval_query_en": "CISG adoption January 2018 84 countries Table 13.1 United States Common Law Civil Law",
        "answerable": True,
        "expected_answer": "Đã có 84 quốc gia thông qua CISG tính đến tháng 1 năm 2018; Hoa Kỳ được xếp vào hệ thống Thông luật (Common Law).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 140,
                "evidence": "By January 2018, 84 countries had adopted CISG"
            },
            {
                "source_id": SOURCE_ID,
                "page": 141,
                "evidence": "| United States |"
            }
        ]
    },

    # Text (3)
    {
        "id": "bonus-dev-13",
        "split": "dev",
        "category": "Text",
        "question": "Trong vụ việc áp dụng dormant commerce clause ở Chicago, tại sao Tòa Phúc thẩm Hoa Kỳ lại giữ nguyên lệnh cấm sơn xịt (spray paint)?",
        "retrieval_query_en": "dormant commerce clause Chicago spray paint ban upheld graffiti crimes",
        "answerable": True,
        "expected_answer": "Tòa án giữ nguyên lệnh cấm vì lệnh cấm nhằm mục đích giảm thiểu hành vi vẽ bậy (graffiti) và các tội phạm liên quan.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 50,
                "evidence": "ban was intended to reduce graffiti and related crimes."
            }
        ]
    },
    {
        "id": "bonus-dev-14",
        "split": "dev",
        "category": "Text",
        "question": "Trong vụ kiện Crown Castle Inc. v. Fred Nudd Corporation năm 2008, tòa án đã xác định các cột ăng-ten điện thoại di động (monopoles) là hàng hóa (goods) hay bất động sản (realty)?",
        "retrieval_query_en": "Crown Castle v Fred Nudd monopoles goods realty movable",
        "answerable": True,
        "expected_answer": "Tòa án xác định rằng các cột monopoles là hàng hóa (goods) vì chúng được coi là có thể di dời.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 88,
                "evidence": "Ultimately, it was determined that monopoles are goods."
            }
        ]
    },
    {
        "id": "bonus-dev-15",
        "split": "dev",
        "category": "Text",
        "question": "Tim Cook đã phản hồi công khai như thế nào trước những bức xúc của người tiêu dùng Trung Quốc về chính sách bảo hành của Apple?",
        "retrieval_query_en": "Tim Cook public apology warranty China Apple consumer feedback",
        "answerable": True,
        "expected_answer": "Tim Cook đã đưa ra lời xin lỗi công khai, bày tỏ sự lấy làm tiếc về sự hiểu lầm và đưa ra bốn biện pháp Apple dự định thực hiện để giải quyết vấn đề.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 26,
                "evidence": "Tim Cook issued a public apology in which he expressed regret over the misunderstanding"
            }
        ]
    },

    # Thiếu bằng chứng (3)
    {
        "id": "bonus-dev-16",
        "split": "dev",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có nêu số tiền phạt cụ thể bằng đô la Mỹ mà các nhà sản xuất sơn xịt phải nộp trong vụ kiện quy định tại thành phố Chicago không?",
        "retrieval_query_en": "Chicago spray paint fine amount dollar manufacturers penalty",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 50 mô tả quy định cấm sơn xịt của Chicago và việc Tòa Phúc thẩm giữ nguyên lệnh cấm theo dormant commerce clause nhưng không nêu bất kỳ số tiền phạt cụ thể nào."
    },
    {
        "id": "bonus-dev-17",
        "split": "dev",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có cho biết ngày và tháng cụ thể mà phán quyết vụ kiện Crown Castle Inc. v. Fred Nudd Corporation được ban hành vào năm 2008 không?",
        "retrieval_query_en": "Crown Castle Fred Nudd ruling exact day month 2008 decision date",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 88 đề cập năm 2008 của vụ kiện Crown Castle Inc. v. Fred Nudd Corporation nhưng không cung cấp ngày hay tháng cụ thể của phán quyết."
    },
    {
        "id": "bonus-dev-18",
        "split": "dev",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có cung cấp họ tên đầy đủ và tổ chức công tác của ba trọng tài viên được chọn trong kịch bản gia hạn hợp đồng thuê tòa nhà văn phòng thương mại không?",
        "retrieval_query_en": "commercial office building lease renewal arbitrators full names organization affiliation",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 31 chỉ đưa ra ví dụ giả định về chủ tòa nhà văn phòng và người thuê giải quyết tranh chấp giá thuê ($40 và $20/sq ft) qua trọng tài mà không nêu tên người thực hay tổ chức công tác."
    }
]

TEST_QUESTIONS = [
    # Bảng (6)
    {
        "id": "bonus-test-01",
        "split": "test",
        "category": "Bảng",
        "question": "Theo Bảng 4.1, đạo luật cụ thể nào điều chỉnh việc bán thông tin trong hồ sơ của Sở Giao thông (DMV) theo điều khoản thương mại?",
        "retrieval_query_en": "Table 4.1 Driver's Privacy Protection Act DPPA DMV Department of Motor Vehicles",
        "answerable": True,
        "expected_answer": "Đạo luật Bảo vệ Quyền riêng tư của Người lái xe (Driver's Privacy Protection Act - DPPA).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 51,
                "evidence": "The Driver's Privacy Protection Act (DPPA) regulates the sale of information contained in the Department of Motor Vehicles' (DMV's) records."
            }
        ]
    },
    {
        "id": "bonus-test-02",
        "split": "test",
        "category": "Bảng",
        "question": "Trong Bảng 4.2, giá trị tiền tệ tối thiểu được quy định đối với các vụ kiện thông thường để công dân có quyền được bồi thẩm đoàn xét xử theo Tu chính án thứ Bảy là bao nhiêu?",
        "retrieval_query_en": "Table 4.2 Seventh Amendment trial by jury common lawsuits monetary value $20",
        "answerable": True,
        "expected_answer": "Giá trị tiền tệ tối thiểu là $20 theo Tu chính án thứ Bảy.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 52,
                "evidence": "States that citizens have the right to a trial by jury for common lawsuits involving monetary value of $20."
            }
        ]
    },
    {
        "id": "bonus-test-03",
        "split": "test",
        "category": "Bảng",
        "question": "Theo Bảng 6.1 về phân định chức năng trong tố tụng bồi thường ngoài hợp đồng (tort), chủ thể nào quyết định vấn đề thực tế 'What happened' và 'The damages suffered by the plaintiff'?",
        "retrieval_query_en": "Table 6.1 tort litigation Judge Jury Questions of Fact What happened damages suffered",
        "answerable": True,
        "expected_answer": "Bồi thẩm đoàn (The Jury) là chủ thể quyết định các câu hỏi về thực tế (Questions of Fact), bao gồm những gì đã xảy ra và các thiệt hại mà nguyên đơn gánh chịu.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 68,
                "evidence": "What happened"
            },
            {
                "source_id": SOURCE_ID,
                "page": 68,
                "evidence": "The damages suffered by the plaintiff"
            }
        ]
    },
    {
        "id": "bonus-test-04",
        "split": "test",
        "category": "Bảng",
        "question": "Theo Bảng 8.2 về các điều khoản để ngỏ theo UCC, điều khoản mặc định khi hợp đồng không nêu thời hạn thanh toán (Payment) là gì và theo điều khoản UCC nào?",
        "retrieval_query_en": "Table 8.2 UCC open term payment default provision time and place buyer receive goods UCC 2-310(a)",
        "answerable": True,
        "expected_answer": "Thanh toán đến hạn tại thời điểm và địa điểm mà người mua nhận hàng ('due at the time and place at which the buyer is to receive the goods'), căn cứ UCC 2-310(a).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 89,
                "evidence": "| Payment | If payment is not named, default is \"due at the time and place at which the buyer is to receive the goods.\" | UCC 2-310(a) |"
            }
        ]
    },
    {
        "id": "bonus-test-05",
        "split": "test",
        "category": "Bảng",
        "question": "Theo Bảng 8.4, khi người mua áp dụng biện pháp thay thế hàng hóa (obtain cover) khi có vi phạm hợp đồng theo UCC, ba yêu cầu bắt buộc đối với hàng thay thế là gì?",
        "retrieval_query_en": "Table 8.4 Obtain cover buyer remedies UCC substitutes reasonable without delay good faith",
        "answerable": True,
        "expected_answer": "Hàng thay thế phải hợp lý (reasonable), được mua không chậm trễ (acquired without delay), và được mua một cách thiện chí (obtained in good faith).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 94,
                "evidence": "However, substitutes must be reasonable, acquired without delay, and obtained in good faith."
            }
        ]
    },
    {
        "id": "bonus-test-06",
        "split": "test",
        "category": "Bảng",
        "question": "Trong Bảng 13.1, Pháp (France) và Nhật Bản (Japan) được phân loại vào hệ thống Thông luật (Common Law) hay Dân luật (Civil Law)?",
        "retrieval_query_en": "Table 13.1 Common Law Civil Law France Japan legal systems",
        "answerable": True,
        "expected_answer": "Cả Pháp và Nhật Bản đều được phân loại vào hệ thống Dân luật (Civil Law Systems).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 141,
                "evidence": "| Kenya | France |"
            },
            {
                "source_id": SOURCE_ID,
                "page": 141,
                "evidence": "| United States | Japan |"
            }
        ]
    },

    # Ảnh, sơ đồ (5)
    {
        "id": "bonus-test-07",
        "split": "test",
        "category": "Ảnh, sơ đồ",
        "question": "Tiêu đề chính thức xuất hiện ở đầu sơ đồ các bánh răng liên kết trong Hình 13.3 là gì?",
        "retrieval_query_en": "Figure 13.3 title diagram interlocking gears Sources of International Law",
        "answerable": True,
        "expected_answer": "Tiêu đề chính thức của sơ đồ là 'Sources of International Law' (Các nguồn của luật quốc tế).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 137,
                "evidence": "Diagram Title: 'Sources of International Law'."
            }
        ]
    },
    {
        "id": "bonus-test-08",
        "split": "test",
        "category": "Ảnh, sơ đồ",
        "question": "Theo chú thích Hình 6.6, nếu phanh xe không hoạt động như mong đợi thì đó có thể là hậu quả của loại lỗi nào dẫn đến trách nhiệm sản phẩm (product liability)?",
        "retrieval_query_en": "Figure 6.6 brakes do not work manufacturing defect product liability",
        "answerable": True,
        "expected_answer": "Đó có thể là hậu quả của khuyết tật / lỗi chế tạo (manufacturing defect).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 73,
                "evidence": "If brakes do not work like they are supposed to, it could be the result of a manufacturing defect that would result in product liability."
            }
        ]
    },
    {
        "id": "bonus-test-09",
        "split": "test",
        "category": "Ảnh, sơ đồ",
        "question": "Ai là tác giả của bức ảnh nổi tiếng chụp Florence Owens Thompson cùng các con vào năm 1936 tại California trong Hình 14.3, và bức ảnh minh họa bối cảnh xã hội dẫn đến đạo luật nào?",
        "retrieval_query_en": "Figure 14.3 Florence Owens Thompson 1936 California Dorothea Lange Securities Exchange Act of 1934",
        "answerable": True,
        "expected_answer": "Tác giả bức ảnh là Dorothea Lange; bức ảnh phản ánh tình trạng bất ổn kinh tế - xã hội thúc đẩy Quốc hội ban hành Đạo luật Giao dịch Chứng khoán năm 1934 (Securities Exchange Act of 1934).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 149,
                "evidence": "Florence Owens Thompson and her children were living on frozen vegetables and birds they killed in this famous photograph taken in 1936 in California. (Credit: Dorothea Lange/ wikimedia/ License: Public Domain)"
            }
        ]
    },
    {
        "id": "bonus-test-10",
        "split": "test",
        "category": "Ảnh, sơ đồ",
        "question": "Trong Hình 2.5, các chuyên gia hòa giải đang xem xét lợi ích của loài động vật nào để hỗ trợ quá trình hòa giải?",
        "retrieval_query_en": "Figure 2.5 mediation experts therapy dogs canine-assisted mediation",
        "answerable": True,
        "expected_answer": "Chó trị liệu (therapy dogs) hỗ trợ hòa giải (canine-assisted mediation).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 29,
                "evidence": "Mediation experts are considering the benefits of therapy dogs for canine-assisted mediation."
            }
        ]
    },
    {
        "id": "bonus-test-11",
        "split": "test",
        "category": "Ảnh, sơ đồ",
        "question": "Trong Hình 10.4, cơ quan quản lý hành chính nào của Hoa Kỳ được nêu là giám sát tính an toàn và hiệu quả của thuốc?",
        "retrieval_query_en": "Figure 10.4 Food and Drug Administration FDA safety and effectiveness of medication",
        "answerable": True,
        "expected_answer": "Cục Quản lý Thực phẩm và Dược phẩm Hoa Kỳ (Food and Drug Administration - FDA).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 113,
                "evidence": "The Food and Drug Administration (FDA) oversees the safety and effectiveness of medication."
            }
        ]
    },

    # Biểu đồ (5)
    {
        "id": "bonus-test-12",
        "split": "test",
        "category": "Biểu đồ",
        "question": "Trên biểu đồ phong cách đàm phán Hình 2.3, phong cách nào có đặc điểm là mức độ quan tâm đến bản thân thấp (Low Concern for Self) nhưng quan tâm đến đối phương cao (High Concern for Others)?",
        "retrieval_query_en": "Figure 2.3 negotiation chart Low Concern for Self High Concern for Others Yielding",
        "answerable": True,
        "expected_answer": "Phong cách nhượng bộ (Yielding).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 25,
                "evidence": "- Top-Left quadrant: 'Yielding' style (Low Concern for Self, High Concern for Others)."
            }
        ]
    },
    {
        "id": "bonus-test-13",
        "split": "test",
        "category": "Biểu đồ",
        "question": "Trong biểu đồ Hình 2.3, phong cách đàm phán nào nằm ở góc phần tư dưới cùng bên phải với đặc trưng mức quan tâm đến bản thân cao (High) và mức quan tâm đến người khác thấp (Low)?",
        "retrieval_query_en": "Figure 2.3 negotiation styles bottom right quadrant High Concern for Self Low Concern for Others Forceful",
        "answerable": True,
        "expected_answer": "Phong cách áp đặt / quyết liệt (Forceful).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 25,
                "evidence": "- Bottom-Right quadrant: 'Forceful' style (High Concern for Self, Low Concern for Others)."
            }
        ]
    },
    {
        "id": "bonus-test-14",
        "split": "test",
        "category": "Biểu đồ",
        "question": "Trong biểu đồ Hình 2.3, hình tròn ở trung tâm thể hiện phong cách đàm phán nào với mức độ quan tâm trung bình cho cả hai phía?",
        "retrieval_query_en": "Figure 2.3 negotiation styles center circle Compromising medium concern",
        "answerable": True,
        "expected_answer": "Phong cách thỏa hiệp (Compromising).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 25,
                "evidence": "- Center circle: 'Compromising' style (Intermediate / Medium Concern for Self, Medium Concern for Others)."
            }
        ]
    },
    {
        "id": "bonus-test-15",
        "split": "test",
        "category": "Biểu đồ",
        "question": "Theo lưu đồ 4 bước kiểm tra phát ngôn thương mại trong Hình 4.3, nếu câu trả lời ở Bước 1 là CÓ (phát ngôn liên quan hoạt động bất hợp pháp hoặc gây hiểu lầm) thì kết luận pháp lý là gì?",
        "retrieval_query_en": "Figure 4.3 flowchart Step 1 YES illegal misleading Speech is NOT PROTECTED",
        "answerable": True,
        "expected_answer": "Phát ngôn KHÔNG ĐƯỢC bảo vệ bởi Tu chính án thứ Nhất ('Speech is NOT PROTECTED by the First Amendment').",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 53,
                "evidence": "- If YES -> 'Speech is NOT PROTECTED by the First Amendment'."
            }
        ]
    },
    {
        "id": "bonus-test-16",
        "split": "test",
        "category": "Biểu đồ",
        "question": "Theo lưu đồ Hình 4.3, tại Bước 4 ('Is the regulation more extensive than necessary to serve the government interest?'), nếu câu trả lời là KHÔNG (NO) thì phát ngôn có được bảo vệ bởi Tu chính án thứ Nhất không?",
        "retrieval_query_en": "Figure 4.3 flowchart Step 4 NO regulation more extensive than necessary NOT PROTECTED",
        "answerable": True,
        "expected_answer": "Nếu câu trả lời là KHÔNG (NO) ở Bước 4, phát ngôn KHÔNG ĐƯỢC bảo vệ bởi Tu chính án thứ Nhất ('Speech is NOT PROTECTED by the First Amendment').",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 53,
                "evidence": "- If NO -> 'Speech is NOT PROTECTED by the First Amendment'."
            }
        ]
    },

    # Multi-hop (4)
    {
        "id": "bonus-test-17",
        "split": "test",
        "category": "Multi-hop",
        "question": "Ở trang 52, vụ án nổi tiếng nào tại Tối cao Pháp viện đã thiết lập bài kiểm tra 4 bước đối với phát ngôn thương mại, và ở trang 53, các quy định thương mại cần vượt qua phép thử nào theo substantive due process?",
        "retrieval_query_en": "Hudson Gas Electric commercial speech four-part test substantive due process rational-basis test",
        "answerable": True,
        "expected_answer": "Vụ án thiết lập bài kiểm tra 4 bước đối với phát ngôn thương mại là Hudson Gas & Electric Corp v. Public Service Commission of New York; các quy định cần đáp ứng phép thử cơ sở hợp lý (rational-basis test).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 52,
                "evidence": "Hudson Gas & Electric Corp v. Public Service Commission of New York, a four-part test has been established to determine whether commercial speech should be regulated"
            },
            {
                "source_id": SOURCE_ID,
                "page": 53,
                "evidence": "regulations are required to meet the rational-basis test."
            }
        ]
    },
    {
        "id": "bonus-test-18",
        "split": "test",
        "category": "Multi-hop",
        "question": "Theo Mục 2-105 của UCC (trang 88), hàng hóa được định nghĩa như thế nào, và trong Bảng 8.1 (trang 89), ví dụ nào được nêu cho phân loại một người làm việc cho người bán hàng?",
        "retrieval_query_en": "UCC Section 2-105 definition goods tangible movable Table 8.1 employee at a grocery retailer",
        "answerable": True,
        "expected_answer": "Hàng hóa là các vật phẩm hữu hình có thể di dời tại thời điểm xác định vào hợp đồng mua bán; ví dụ trong Bảng 8.1 là nhân viên tại một cửa hàng bán lẻ tạp hóa (An employee at a grocery retailer).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 88,
                "evidence": "Goods are defined in Section 2-105 of the UCC as tangible items “which are movable at the time of identification to the contract for sale.”"
            },
            {
                "source_id": SOURCE_ID,
                "page": 89,
                "evidence": "A person who works for a person who sells goods An employee at a grocery retailer"
            }
        ]
    },
    {
        "id": "bonus-test-19",
        "split": "test",
        "category": "Multi-hop",
        "question": "Trong Bảng 6.1 (trang 68), ai là người quyết định các vấn đề pháp lý (Issues of Law), và ở trang 74, nếu nguyên đơn bị thương do chân trần không giữ được gỗ khi dùng cưa máy thì họ có thể chịu trách nhiệm gì?",
        "retrieval_query_en": "Table 6.1 Judge Decides Issues of Law chainsaw bare foot comparative negligence",
        "answerable": True,
        "expected_answer": "Thẩm phán (The Judge) quyết định các vấn đề pháp lý; nguyên đơn có thể chịu trách nhiệm về lỗi bất cẩn so sánh (comparative negligence).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 68,
                "evidence": "| The Judge Decides Issues of Law | The Jury Decides Questions of Fact |"
            },
            {
                "source_id": SOURCE_ID,
                "page": 74,
                "evidence": "he could be responsible for comparative negligence."
            }
        ]
    },
    {
        "id": "bonus-test-20",
        "split": "test",
        "category": "Multi-hop",
        "question": "Ở trang 140, công ước CISG không áp dụng cho những loại hình bán hàng hoặc hợp đồng nào, và trong Bảng 13.1 (trang 141), hãy nêu tên ít nhất hai quốc gia châu Phi thuộc hệ thống Thông luật (Common Law)?",
        "retrieval_query_en": "CISG limits consumer sales contracts for services Table 13.1 African nations Common Law Nigeria Ghana Kenya Zambia",
        "answerable": True,
        "expected_answer": "CISG không áp dụng cho việc bán hàng cho người tiêu dùng (consumer sales) hoặc các hợp đồng dịch vụ (contracts for services); hai quốc gia châu Phi thuộc Thông luật trong Bảng 13.1 có thể là Nigeria, Ghana, Kenya hoặc Zambia.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 140,
                "evidence": "CISG does not apply to consumer sales or contracts for services"
            },
            {
                "source_id": SOURCE_ID,
                "page": 141,
                "evidence": "| Ghana |"
            },
            {
                "source_id": SOURCE_ID,
                "page": 141,
                "evidence": "| Nigeria |"
            },
            {
                "source_id": SOURCE_ID,
                "page": 141,
                "evidence": "| Kenya |"
            },
            {
                "source_id": SOURCE_ID,
                "page": 141,
                "evidence": "| Zambia |"
            }
        ],
        "evidence_groups": [
            {"min_matches": 1, "gold_indices": [0]},
            {"min_matches": 2, "gold_indices": [1, 2, 3, 4]}
        ]
    },

    # Text (4)
    {
        "id": "bonus-test-21",
        "split": "test",
        "category": "Text",
        "question": "Theo ngoại lệ pervasive-regulation đối với Tu chính án thứ Tư, đạo luật năm 1977 nào cho phép các cơ quan y tế công cộng khám xét không cần lệnh đối với các mỏ đá (stone quarries)?",
        "retrieval_query_en": "pervasive-regulation warrantless searches stone quarries Federal Mine Safety and Health Act of 1977",
        "answerable": True,
        "expected_answer": "Đạo luật An toàn và Sức khỏe Mỏ Liên bang năm 1977 (Federal Mine Safety and Health Act of 1977).",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 53,
                "evidence": "Federal Mine Safety and Health Act of 1977."
            }
        ]
    },
    {
        "id": "bonus-test-22",
        "split": "test",
        "category": "Text",
        "question": "Theo Đạo luật Trả lương Bình đẳng (Equal Pay Act - EPA), trong bốn biện pháp bào chữa khẳng định của người sử dụng lao động, biện pháp nào được viện dẫn thường xuyên nhất và gây tranh cãi gay gắt nhất?",
        "retrieval_query_en": "Equal Pay Act EPA four affirmative defenses factor other than sex frequently invoked controversy",
        "answerable": True,
        "expected_answer": "Biện pháp bào chữa dựa trên 'bất kỳ yếu tố nào khác ngoài giới tính' ('factor other than sex').",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 107,
                "evidence": "“factor other than sex” defense has been invoked most frequently and has been the subject of intense debate and controversy."
            }
        ]
    },
    {
        "id": "bonus-test-23",
        "split": "test",
        "category": "Text",
        "question": "Theo Nguyên tắc Lễ nhượng Quốc tế (Principle of Comity), tại sao tòa án Hoa Kỳ nhiều khả năng sẽ công nhận một hợp đồng kinh doanh được soạn thảo tại Anh?",
        "retrieval_query_en": "Principle of Comity US court business contract England United Kingdom procedures consistent",
        "answerable": True,
        "expected_answer": "Bởi vì các thủ tục và quy trình pháp lý của Vương quốc Anh nhất quán và tương thích với các thủ tục của Hoa Kỳ.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 140,
                "evidence": "since the United Kingdom’s legal procedures are consistent with U.S. procedures"
            }
        ]
    },
    {
        "id": "bonus-test-24",
        "split": "test",
        "category": "Text",
        "question": "Trong học thuyết Hành vi Quốc gia (Act of State Doctrine), công ty dầu mỏ nào của Brazil được nêu làm ví dụ mà Hoa Kỳ sẽ không khởi kiện về cáo buộc ấn định giá?",
        "retrieval_query_en": "Act of State Doctrine Brazilian oil company price fixing Petrobras",
        "answerable": True,
        "expected_answer": "Công ty dầu mỏ Petrobras của Brazil.",
        "gold": [
            {
                "source_id": SOURCE_ID,
                "page": 140,
                "evidence": "Petrobras, a Brazilian oil company, alleging price fixing, since the act of pricing oil occurs in Brazil"
            }
        ]
    },

    # Thiếu bằng chứng (6)
    {
        "id": "bonus-test-25",
        "split": "test",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có nêu số tiền bồi thường thiệt hại cụ thể bằng USD mà công ty Duke Power Co. phải chi trả cho nguyên đơn Willie Griggs trong vụ kiện phân biệt đối xử không?",
        "retrieval_query_en": "Griggs Duke Power exact compensatory damage dollar amount paid plaintiff",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 105 đề cập vụ kiện Griggs v. Duke Power Co. và tiêu chuẩn disparate impact đối với bài thi trí tuệ, nhưng không nêu bất kỳ số tiền bồi thường cụ thể nào."
    },
    {
        "id": "bonus-test-26",
        "split": "test",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có cung cấp điều lệ công ty đầy đủ hoặc danh sách các thành viên hội đồng quản trị của Crown Castle Inc. tại thời điểm diễn ra vụ kiện năm 2008 không?",
        "retrieval_query_en": "Crown Castle Inc corporate bylaws board of directors list 2008 litigation",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 88 đề cập vụ tranh chấp Crown Castle Inc. v. Fred Nudd Corporation về cột viễn thông nhưng không bao gồm điều lệ hoặc danh sách thành viên hội đồng quản trị."
    },
    {
        "id": "bonus-test-27",
        "split": "test",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có ghi rõ ngày và tháng chính xác trong năm 2018 khi Trung Quốc tuyên bố Hoa Kỳ phát động cuộc chiến thương mại lớn nhất trong lịch sử kinh tế không?",
        "retrieval_query_en": "China accusation US trade war economic history exact calendar date day month 2018 BBC",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 141 trích dẫn phát biểu của Trung Quốc năm 2018 qua nguồn (BBC, 2018) nhưng không ghi ngày hoặc tháng cụ thể."
    },
    {
        "id": "bonus-test-28",
        "split": "test",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có nêu mức thù lao theo giờ chính xác mà trọng tài viên đã tính phí trong ví dụ hòa giải gia hạn hợp đồng thuê văn phòng ở trang 31 không?",
        "retrieval_query_en": "commercial office building lease arbiter hourly billing rate fee charged",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 31 đề cập đến giá thuê ($40, $20, $30 trên mỗi foot vuông) nhưng không đề cập đến mức thù lao tính theo giờ của trọng tài viên."
    },
    {
        "id": "bonus-test-29",
        "split": "test",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có thống kê số lượng chính xác các mỏ đá đã bị các cơ quan y tế công cộng thanh tra không cần lệnh trong năm 2025 theo Đạo luật năm 1977 không?",
        "retrieval_query_en": "exact number of stone quarries inspected warrantless search 2025 statistics",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 53 chỉ nêu nguyên tắc cho phép khám xét không cần lệnh đối với mỏ đá theo Đạo luật 1977 mà không cung cấp số liệu thống kê về số lượng mỏ bị thanh tra năm 2025."
    },
    {
        "id": "bonus-test-30",
        "split": "test",
        "category": "Thiếu bằng chứng",
        "question": "Tài liệu có cho biết số tuổi chính xác của Florence Owens Thompson khi bà được chụp hình trong bức ảnh nổi tiếng năm 1936 không?",
        "retrieval_query_en": "Florence Owens Thompson exact age in 1936 photograph Dorothea Lange",
        "answerable": False,
        "expected_behavior": "search_and_abstain",
        "absence_reason": "Trang 149 miêu tả hoàn cảnh của bà Florence Owens Thompson và các con trong bức ảnh năm 1936 của Dorothea Lange nhưng không nêu số tuổi chính xác của bà."
    }
]

def main():
    chunks = json.loads(Path('data/bonus_chunks.json').read_text(encoding='utf-8'))
    all_questions = DEV_QUESTIONS + TEST_QUESTIONS

    print(f"Total dev questions: {len(DEV_QUESTIONS)}")
    print(f"Total test questions: {len(TEST_QUESTIONS)}")

    # Validate schema and evidence hits
    validate(chunks, all_questions)
    print("ALL QUESTIONS VALIDATED SUCCESSFULLY AGAINST BONUS CHUNKS!")

    out_path = Path('data/bonus_questions.json')
    out_path.write_text(json.dumps(all_questions, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Wrote questions to {out_path}")

if __name__ == '__main__':
    main()
