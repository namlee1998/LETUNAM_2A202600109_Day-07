# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** LÊ TÚ NAM
**Nhóm:** C5
**Ngày:** 10/4/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Cosine similarity cao (gần 1.0) có nghĩa là hai vector đang chỉ về cùng một hướng . Khi đó, góc giữa chúng trong không gian vecto  rất nhỏ.

**Ví dụ HIGH similarity:**
- Sentence A: Anh ấy mua 1 chiếc xe hơi mới
- Sentence B: Ông ấy tậu 1 chiến xe hơi mới
- Tại sao tương đồng: cùng đối tượng: anh ấy và ông ấy(đều là đàn ông), xe hơi. 
Cùng trạng thái: mới.
Cùng số lượng: 1

**Ví dụ LOW similarity:**
- Sentence A: Con mèo đang nằm ngủ trên ghế sofa.
- Sentence B: Phương trình bậc 2 có 2 nghiệm phân biệt.
- Tại sao khác: Về đối tượng, trạng thái,số lượng đều khác biệt.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Vì nếu dùng Euclidean: 
câu ngắn và dài dù cùng nghĩa vẫn sẽ được coi là khác nhau
2 câu khác nghĩa nhưng chỉ cần ngắn bằng nhau thì được coi là giống nhau.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
*stride=chunk_size−overlap = 500−50=450
*chunks= ((document_lenght -chunk size)/stride) + 1 = ((10000−500​)/450) +1 = 22
*Đáp án= 22

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
Overlap tăng → stride giảm → số chunk tăng
Giúp hệ thống RAG hiểu ngữ cảnh tốt hơn, tránh mất ngữ cảnh tại ranh giới các chunk khi dùng Slide window.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:**  Bộ luật hình sự Việt Nam 2015

**Tại sao nhóm chọn domain này?**
Vì đây là văn bản có cấu trúc rõ ràng, dễ xác định ranh giới chunk, Bộ luật được tổ chức theo cấu trúc phân cấp nên giữ được ngữ cảnh logic của điều luật.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Bộ luật hình sụ | Cổng thông tin chính phủ| 562623|  Hiệu lực của bộ luật hình sự,Điều khoản cơ bản, Tội phạm|
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| document_title|string | "Bộ luật Hình sự 2015"| Giúp xác định chính xác tài liệu nguồn khi trả lời|
| law_type| string| "criminal_law"| Cho phép lọc theo loại luật (hình sự, dân sự, hành chính)|

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Bộ luật Hình sự | FixedSizeChunker (`fixed_size`) | 1147|499.85 | K giu dươc|
| Bộ luật Hình sự | SentenceChunker (`by_sentences`) | 671|835 | Giu dươc context|
| Bộ luật Hình sự | RecursiveChunker (`recursive`) |1450 |386 | Giu duoc context|

### Strategy Của Tôi

**Loại:** [ RecursiveChunker]

**Mô tả cách hoạt động:**
Recursive chunking chia văn bản theo cấu trúc ngữ nghĩa từ lớn → nhỏ. theo dấu hiệu ["\n\n", "\n", ".", " ", ""]. Nghĩa là paragraph → sentence → word → character.

**Tại sao tôi chọn strategy này cho domain nhóm?**
Văn bản luật có cấu trúc rõ ràng. Giữ ngữ cảnh pháp lý. Tăng chất lượng retrieval trong RAG.

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | SentenceChunker|  671|835 | Giữ được context|
| | **của tôi** |  RecursiveChunker (`recursive`) |1450 |386 | Giữ được context|

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tú nam | RecursiveChunker| 4.2| Giữ ngữ cảnh tốt vì chia theo cấu trúc văn bản (paragraph → sentence → word). Phù hợp với tài liệu có cấu trúc như luật. Giảm việc cắt giữa câu.| Phức tạp hơn khi triển khai, đôi khi chunk không đều kích thước, có thể tạo nhiều chunk hơn baseline.|
| Hữu Hưng | RecursiveChunker, chunk_size=500 | 4 | Tôn trọng ranh giới Điều/khoản (`\n\n`→`\n`), chunk coherent với cấu trúc pháp lý | 1447 chunks nhỏ (avg 387 ký tự) — nhiều chunk quá, score dàn đều|
| Khánh Nam | RecursiveChunker, chunk_size=200 | 6 | Điểm mạnh: Chia đoạn nhỏ giúp tăng độ chính xác khi truy xuất các đoạn thông tin ngắn, giảm nhiễu trong mỗi chunk, phù hợp với dữ liệu có cấu trúc rõ ràng. | Điểm yếu: Chunk size 200 khá nhỏ nên dễ làm mất ngữ cảnh giữa các đoạn, tăng số lượng chunk khiến retrieval tốn tài nguyên hơn, có thể giảm hiệu quả với nội dung dài cần nhiều context. |
| Hiếu| SentenceChunker | 4.5| Chia đúng theo câu nên ngữ nghĩa rõ ràng, dễ hiểu với embedding model. Chunk thường sạch và ít bị cắt giữa ý.|Có thể mất context nếu thông tin nằm ở nhiều câu liên tiếp. Một số câu quá ngắn hoặc quá dài gây mất cân bằng chunk size. |
|Phúc| FixedSizeChunker| 3.5| Rất đơn giản, dễ implement, tốc độ xử lý nhanh. Chunk size ổn định nên dễ kiểm soát token.| Không giữ ngữ cảnh tốt, dễ cắt giữa câu hoặc điều luật, làm giảm chất lượng embedding và retrieval.|
| Quân | RecursiveChunker, chunk_size=200 | 7 |giữ ngữ cảnh tốt vì tận dụng được cấu trúc đơn vị của câu|khó implement hơn tương đối và có chi phí tính toán cao hơn|


**Strategy nào tốt nhất cho domain này? Tại sao?**
Recursive chunking là strategy phù hợp nhất cho domain văn bản pháp luật vì nó chia văn bản theo cấu trúc tự nhiên như đoạn và câu, giúp giữ nguyên ngữ cảnh của các điều luật. Điều này cải thiện chất lượng embedding và tăng độ chính xác của retrieval trong hệ thống RAG.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
Dùng regex lookbehind (?<=[\.\!\?])\s+ để tách câu tại vị trí sau dấu . ! ? mà không xóa mất dấu câu.
Xử lý edge case: loại bỏ khoảng trắng đầu/cuối =strip() if s.strip()

**`RecursiveChunker.chunk` / `_split`** — approach:
Hàm hoạt dộng theo cơ chế đệ quy.
Base case 1 – Text đã đủ nhỏ
Base case 2 – Hết separator
Trường hợp separator = ""

### EmbeddingStore

**`add_documents` + `search`** — approach:
Lưu trữ vào chromaDB, nếu không có thì lưu vào memory
_dot(vec_a, vec_b) / (mag_a * mag_b) 

**`search_with_filter` + `delete_document`** — approach:
Dùng Pre_filter
xóa document bằng cách lọc lại toàn bộ danh sách _store (list filtering)

### KnowledgeBaseAgent

**`answer`** — approach:
prompt = (
    "Use the following context to answer the question.\n"
    "If the answer is not contained in the context, say 'I don't know'.\n\n"
    "Context:\n"
    "{context}\n\n"
    "Question: {question}\n"
    "Answer:"
)
lấy context từ vector store rồi inject vào prompt để gửi cho LLM.

### Test Results

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                         [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                  [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                           [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                            [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                 [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                 [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                       [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                        [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                      [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                        [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                        [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                   [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                               [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                         [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                    [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                              [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                    [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                        [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                          [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                            [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                  [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                       [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                         [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                             [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                          [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                   [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                  [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                             [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                         [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                    [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                        [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                              [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                        [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                     [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                   [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                  [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                      [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                 [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                          [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                    [100%]

======================================================== 42 passed in 0.68s ========================================================
```

**Số tests pass:** 42 /42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A| Sentence B| Dự đoán | Actual Score | Đúng? |

| 1    | Trộm cắp tài sản là hành vi chiếm đoạt tài sản của người khác.| Tội trộm cắp tài sản là hành vi lấy tài sản của người khác trái phép. | high| 0.89| ✔|

| 2    | Người phạm tội có thể bị phạt tù từ 6 tháng đến 3 năm.| Hình phạt tù có thể áp dụng đối với người phạm tội.| high|0.82| ✔|

| 3    | Tòa án quyết định hình phạt dựa trên tính chất hành vi phạm tội.| Người phạm tội phải bồi thường thiệt hại cho nạn nhân.| low| 0.36| ✔|

| 4    | Điều 102 quy định về quyết định hình phạt đối với người dưới 18 tuổi.| Luật hình sự có nhiều quy định về trách nhiệm hình sự.| low| 0.41| ✔|

| 5    | Người dưới 18 tuổi phạm tội có thể được giảm nhẹ hình phạt.| Người chưa thành niên phạm tội có thể được xem xét giảm án.| high| 0.86| ✔|


**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
Kết quả bất ngờ nhất là Pair 4. Kết quả bất ngờ nhất thường là Pair 4.
Embeddings không chỉ dựa vào từ giống nhau. Chúng học semantic relationships.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

5 Benchmark Queries + Gold Answers
#	Query	Gold Answer	Chunk chứa thông tin	Loại query
1	Người từ đủ 14 tuổi đến dưới 16 tuổi phải chịu trách nhiệm hình sự về những tội nào?	Tội giết người, cố ý gây thương tích, hiếp dâm, hiếp dâm người dưới 16 tuổi, cưỡng dâm người từ đủ 13 đến dưới 16 tuổi, cướp tài sản, bắt cóc nhằm chiếm đoạt tài sản; và các tội phạm rất nghiêm trọng, đặc biệt nghiêm trọng tại các Điều 143, 150, 151, 170, 171, 173, 178, 248-252, 265, 266, 285-287, 289, 290, 299, 303, 304 (Điều 12)

2	Trộm cắp tài sản trị giá 500 triệu đồng trở lên thì bị phạt tù bao nhiêu năm?	Phạt tù từ 12 năm đến 20 năm (Điều 173, khoản 4)

3	Các tình tiết giảm nhẹ trách nhiệm hình sự bao gồm những gì?	22 tình tiết tại Điều 51 khoản 1, gồm: ngăn chặn/giảm bớt tác hại; tự nguyện bồi thường; vượt quá phòng vệ chính đáng; tình thế cấp thiết; bị kích động; hoàn cảnh khó khăn; chưa gây thiệt hại; phạm tội lần đầu ít nghiêm trọng; bị đe dọa/cưỡng bức; phụ nữ có thai; người đủ 70 tuổi; khuyết tật nặng; tự thú; thành khẩn khai báo; lập công chuộc tội... Ngoài ra Tòa án có thể coi đầu thú hoặc tình tiết khác là giảm nhẹ (khoản 2)	Điều 51	

4	Lái xe gây tai nạn chết người rồi bỏ chạy thì bị xử lý thế nào?	Phạt tù từ 3 năm đến 10 năm theo Điều 260 khoản 2 điểm c: "Gây tai nạn rồi bỏ chạy để trốn tránh trách nhiệm hoặc cố ý không cứu giúp người bị nạn"	Điều 260	

5	Tội phạm được phân thành mấy loại và mức phạt tù tối đa của mỗi loại là bao nhiêu?	4 loại theo Điều 9: (1) Ít nghiêm trọng — đến 3 năm tù; (2) Nghiêm trọng — trên 3 đến 7 năm; (3) Rất nghiêm trọng — trên 7 đến 15 năm; (4) Đặc biệt nghiêm trọng — trên 15 đến 20 năm, chung thân hoặc tử hình	Điều 9	

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|

| 1 | Người từ đủ 14 tuổi đến dưới 16 tuổi phải chịu trách nhiệm hình sự về những tội nào? | Điều 12: Quy định người từ 14–16 tuổi chỉ chịu trách nhiệm hình sự đối với một số tội nghiêm trọng như giết người, cướp tài sản, hiếp dâm… | 0.91  | ✔ | Người từ 14 đến dưới 16 tuổi chỉ chịu trách nhiệm hình sự với một số tội nghiêm trọng như giết người, cố ý gây thương tích, hiếp dâm, cướp tài sản… theo Điều 12.|

| 2 | Trộm cắp tài sản trị giá 500 triệu đồng trở lên thì bị phạt tù bao nhiêu năm?| Điều 173 khoản 4: Trộm cắp tài sản trị giá 500 triệu đồng trở lên bị phạt tù từ 12 đến 20 năm.| 0.94| ✔| Trộm cắp tài sản từ 500 triệu đồng trở lên bị phạt tù từ 12–20 năm theo Điều 173 khoản 4|

| 3 | Các tình tiết giảm nhẹ trách nhiệm hình sự bao gồm những gì?| Điều 51: Liệt kê các tình tiết giảm nhẹ như tự nguyện bồi thường, thành khẩn khai báo, phạm tội lần đầu ít nghiêm trọng…| 0.88  | ✔| Có nhiều tình tiết giảm nhẹ như tự nguyện bồi thường thiệt hại, thành khẩn khai báo, phạm tội lần đầu, lập công chuộc tội… theo Điều 51.|

| 4 | Lái xe gây tai nạn chết người rồi bỏ chạy thì bị xử lý thế nào?| Điều 260 khoản 2 điểm c: Gây tai nạn giao thông rồi bỏ chạy để trốn tránh trách nhiệm bị phạt tù từ 3 đến 10 năm.| 0.86| ✔| Hành vi gây tai nạn chết người rồi bỏ chạy có thể bị phạt tù từ 3–10 năm theo Điều 260 khoản 2 điểm c.|

| 5 | Tội phạm được phân thành mấy loại và mức phạt tù tối đa của mỗi loại là bao nhiêu?| Điều 9: Phân loại tội phạm thành 4 loại theo mức độ nghiêm trọng và khung hình phạt tối đa.| 0.90| ✔| Tội phạm được chia thành 4 loại: ít nghiêm trọng (≤3 năm), nghiêm trọng (3–7 năm), rất nghiêm trọng (7–15 năm), đặc biệt nghiêm trọng (>15 năm đến tù chung thân hoặc tử hình).|


**Bao nhiêu queries trả về chunk relevant trong top-3?** 5/ 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
Tôi học được cách các thành viên khác thử nhiều chunking strategies khác nhau (như sentence chunking và fixed-size chunking) để so sánh hiệu quả retrieval. Điều này giúp tôi hiểu rằng việc chọn đúng phương pháp chia văn bản ảnh hưởng rất lớn đến chất lượng kết quả của hệ thống RAG. Ngoài ra, việc kiểm tra edge cases trong quá trình chunking cũng rất quan trọng.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
Tôi học được cách các thành viên khác thử nhiều chunking strategies khác nhau (custom-chunking) để so sánh hiệu quả retrieval. Điều này giúp tôi hiểu rằng việc chọn đúng phương pháp chia văn bản ảnh hưởng rất lớn đến chất lượng kết quả của hệ thống RAG. Ngoài ra, việc kiểm tra edge cases trong quá trình chunking cũng rất quan trọng.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
Tôi sẽ xem xét kĩ càng hơn về mặt lấy data, hiện tại độ tương thích giữa query của user và câu trả lời được lấy ra có score vẫn chưa cao.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5/ 5 |
| Document selection | Nhóm | 10/ 10 |
| Chunking strategy | Nhóm | 15/ 15 |
| My approach | Cá nhân | 10/ 10 |
| Similarity predictions | Cá nhân | 5/ 5 |
| Results | Cá nhân | 10/ 10 |
| Core implementation (tests) | Cá nhân | 30/ 30 |
| Demo | Nhóm | 5/ 5 |
| **Tổng** | | **90/ 90** |
