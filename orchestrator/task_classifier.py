import re

def classify_task(requirement):
    req_lower = requirement.lower()
    
    # Keywords patterns
    test_fix_patterns = [
        r"pytest", r"테스트\s*실패", r"test\s*failed", r"테스트\s*에러", r"테스트\s*오류"
    ]
    code_fix_patterns = [
        r"버그", r"오류", r"예외", r"traceback", r"실패", r"fix", r"수정", r"해결"
    ]
    doc_patterns = [
        r"readme", r"문서", r"설명", r"가이드", r"md", r"markdown", r"주석"
    ]
    refactor_patterns = [
        r"리팩터링", r"리팩토링", r"refactor", r"구조\s*개선", r"모듈\s*분리", r"코드\s*정리"
    ]
    large_context_patterns = [
        r"전체\s*구조\s*검토", r"대용량\s*코드베이스", r"대용량\s*코드베이스\s*분석", r"코드베이스\s*분석"
    ]
    final_review_patterns = [
        r"리뷰", r"검토", r"diff\s*검토", r"최종\s*검토"
    ]

    matched_type = None
    reason = "매칭되는 키워드가 없어 기본값 배정"
    confidence = 0.5
    
    # Classify priority logic
    if any(re.search(pat, req_lower) for pat in test_fix_patterns):
        matched_type = "test_fix"
        reason = "요구사항에서 pytest 또는 테스트 실패 키워드가 발견되어 test_fix로 판정했습니다."
        confidence = 0.9
    elif any(re.search(pat, req_lower) for pat in refactor_patterns):
        matched_type = "refactor"
        reason = "요구사항에서 리팩터링 또는 구조 개선 키워드가 발견되어 refactor로 판정했습니다."
        confidence = 0.95
    elif any(re.search(pat, req_lower) for pat in doc_patterns):
        matched_type = "documentation"
        reason = "요구사항에서 README, 문서, markdown 키워드가 발견되어 documentation으로 판정했습니다."
        confidence = 0.95
    elif any(re.search(pat, req_lower) for pat in large_context_patterns):
        matched_type = "large_context_review"
        reason = "요구사항에서 전체 구조 검토 또는 대용량 코드베이스 분석 키워드가 발견되어 large_context_review로 판정했습니다."
        confidence = 0.9
    elif any(re.search(pat, req_lower) for pat in final_review_patterns):
        matched_type = "final_review"
        reason = "요구사항에서 리뷰 또는 최종 검토 키워드가 발견되어 final_review로 판정했습니다."
        confidence = 0.9
    elif any(re.search(pat, req_lower) for pat in code_fix_patterns):
        matched_type = "python_code_fix"
        reason = "요구사항에서 버그, 오류, 예외 수정 키워드가 발견되어 python_code_fix로 판정했습니다."
        confidence = 0.9
    else:
        matched_type = "python_code_fix"
        reason = "요구사항 분석에서 매칭된 키워드가 모호하여 기본 코딩 작업인 python_code_fix로 Fallback 처리했습니다."
        confidence = 0.4
        
    # Weight inference
    weight_defaults = {
        "documentation": "light",
        "final_review": "light",
        "test_fix": "medium",
        "python_code_fix": "medium",
        "large_context_review": "heavy",
        "refactor": "heavy"
    }
    matched_weight = weight_defaults.get(matched_type, "medium")
    
    # Heavy scale-up keywords
    heavy_up_patterns = [
        r"전체", r"대규모", r"구조\s*변경", r"리팩터링", r"리팩토링", r"파이프라인", r"아키텍처", r"성능", r"장애\s*복구"
    ]
    if any(re.search(pat, req_lower) for pat in heavy_up_patterns):
        matched_weight = "heavy"
        reason += " (요구사항에 대규모/전체/구조 변경 등의 단어가 포함되어 작업 무게를 heavy로 상향 조정했습니다.)"
        
    return matched_type, matched_weight, confidence, reason
