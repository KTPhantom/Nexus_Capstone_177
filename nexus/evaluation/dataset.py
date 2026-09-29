"""
Golden Evaluation Benchmark Dataset.
Contains realistic user prompts for Student and Shopkeeper domains,
graded relevance judgments, and hard negative distractors (CoRNStack - ICLR 2025).
"""

from typing import List, Dict
from pydantic import BaseModel, Field


class EvaluationQuery(BaseModel):
    query_id: str
    query_text: str
    target_domain: str
    relevant_components: Dict[str, int]  # component_id -> relevance grade (3=ideal, 2=good, 1=marginal)
    hard_negatives: List[str] = Field(default_factory=list)
    query_type: str  # "direct_task" | "conversational_intent" | "hard_negative" | "multi_intent"


GOLDEN_BENCHMARK_DATASET: List[EvaluationQuery] = [
    # ==========================
    # STUDENT DOMAIN QUERIES
    # ==========================
    EvaluationQuery(
        query_id="STU-01",
        query_text="I need a 25-minute focus study timer that alerts me when it's time for short and long breaks",
        target_domain="student",
        relevant_components={"student/PomodoroTimer": 3},
        hard_negatives=["student/NotesEditor", "shopkeeper/DailyCashLedger"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="STU-02",
        query_text="Track my semester grades, assign credit weights to my subjects, and calculate my cumulative CGPA and SGPA",
        target_domain="student",
        relevant_components={"student/GradeTracker": 3},
        hard_negatives=["shopkeeper/ProfitMarginCalculator", "student/AssignmentTracker"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="STU-03",
        query_text="Digital flip cards for active recall and spaced repetition to memorize algorithms and definitions for exams",
        target_domain="student",
        relevant_components={"student/FlashcardDeck": 3},
        hard_negatives=["student/NotesEditor", "student/FormulaSheet"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="STU-04",
        query_text="I have multiple homework assignments and lab reports due next week, need to track due dates and submission progress",
        target_domain="student",
        relevant_components={"student/AssignmentTracker": 3},
        hard_negatives=["student/GradeTracker", "shopkeeper/DailySalesReceipt"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="STU-05",
        query_text="Take markdown lecture notes during class with live preview, word count and subject tagging",
        target_domain="student",
        relevant_components={"student/NotesEditor": 3},
        hard_negatives=["student/FlashcardDeck", "student/AssignmentTracker"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="STU-06",
        query_text="Quick reference cheat sheet for math, calculus, and physics formulas with copyable LaTeX equations",
        target_domain="student",
        relevant_components={"student/FormulaSheet": 3},
        hard_negatives=["student/NotesEditor", "shopkeeper/ProfitMarginCalculator"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="STU-07",
        query_text="Format bibliography citations for my research paper into APA, MLA, or IEEE format given author and publication details",
        target_domain="student",
        relevant_components={"student/CitationGenerator": 3},
        hard_negatives=["student/NotesEditor", "shopkeeper/DailySalesReceipt"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="STU-08",
        query_text="How many classes can I safely bunk without falling below the university mandatory 75% attendance threshold?",
        target_domain="student",
        relevant_components={"student/AttendanceTracker": 3},
        hard_negatives=["student/GradeTracker", "student/AssignmentTracker"],
        query_type="conversational_intent",
    ),
    EvaluationQuery(
        query_id="STU-09",
        query_text="Prepare an intense revision workspace: study intervals and memorization cards for upcoming midterms",
        target_domain="student",
        relevant_components={"student/PomodoroTimer": 3, "student/FlashcardDeck": 3, "student/NotesEditor": 2},
        hard_negatives=["shopkeeper/InventoryStockTable"],
        query_type="multi_intent",
    ),
    EvaluationQuery(
        query_id="STU-10",
        query_text="Manage my thesis writing citations and mathematical formula symbols for the capstone final documentation",
        target_domain="student",
        relevant_components={"student/CitationGenerator": 3, "student/FormulaSheet": 3, "student/NotesEditor": 2},
        hard_negatives=["shopkeeper/SupplierContactList"],
        query_type="multi_intent",
    ),

    # ==========================
    # SHOPKEEPER DOMAIN QUERIES
    # ==========================
    EvaluationQuery(
        query_id="SHP-01",
        query_text="Keep a daily cashbook for counter sales, recording cash in hand and UPI payments from GooglePay and PhonePe",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/DailyCashLedger": 3},
        hard_negatives=["student/GradeTracker", "shopkeeper/ProfitMarginCalculator"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="SHP-02",
        query_text="Manage warehouse product stock, monitor SKU counts, and alert me when items fall below reorder threshold",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/InventoryStockTable": 3},
        hard_negatives=["student/AssignmentTracker", "shopkeeper/ExpiryDateAlerts"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="SHP-03",
        query_text="Directory of wholesale distributors, vendor phone numbers, payment credit terms, and pending bills",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/SupplierContactList": 3},
        hard_negatives=["shopkeeper/CustomerUdharKhata", "student/NotesEditor"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="SHP-04",
        query_text="Point of sale barcode scanner to scan item EAN barcodes and instantly fetch price and stock for quick checkout",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/BarcodeScannerInput": 3},
        hard_negatives=["shopkeeper/DailySalesReceipt", "student/FormulaSheet"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="SHP-05",
        query_text="Calculate wholesale cost markup, selling price MRP, and net profit margin after deducting 5% or 18% GST tax",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/ProfitMarginCalculator": 3},
        hard_negatives=["student/GradeTracker", "shopkeeper/DailyCashLedger"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="SHP-06",
        query_text="Monitor dairy and bakery product batches to detect perishable items nearing expiration date and apply clearance discounts",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/ExpiryDateAlerts": 3},
        hard_negatives=["shopkeeper/InventoryStockTable", "student/AssignmentTracker"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="SHP-07",
        query_text="Generate customer tax bill and printed sales receipt with itemized goods, GST breakdown, and total balance",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/DailySalesReceipt": 3},
        hard_negatives=["shopkeeper/DailyCashLedger", "student/CitationGenerator"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="SHP-08",
        query_text="Customer credit ledger (udhar khata) to track who owes money to the shop and send payment reminders via WhatsApp",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/CustomerUdharKhata": 3},
        hard_negatives=["shopkeeper/SupplierContactList", "shopkeeper/DailyCashLedger"],
        query_type="direct_task",
    ),
    EvaluationQuery(
        query_id="SHP-09",
        query_text="I am setting up morning billing: scan barcodes, generate printed tax receipts and record cash in counter",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/BarcodeScannerInput": 3, "shopkeeper/DailySalesReceipt": 3, "shopkeeper/DailyCashLedger": 2},
        hard_negatives=["student/NotesEditor"],
        query_type="multi_intent",
    ),
    EvaluationQuery(
        query_id="SHP-10",
        query_text="Stock restocking day: check low inventory, contact wholesale suppliers and verify pending distributor balances",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/InventoryStockTable": 3, "shopkeeper/SupplierContactList": 3},
        hard_negatives=["student/GradeTracker"],
        query_type="multi_intent",
    ),

    # ==========================
    # HARD NEGATIVES & TRICKY CROSS-DOMAIN QUERIES (CoRNStack Benchmark)
    # ==========================
    EvaluationQuery(
        query_id="HARD-01",
        query_text="Ledger of students and grades with weighted calculations",
        target_domain="student",
        relevant_components={"student/GradeTracker": 3},
        hard_negatives=["shopkeeper/DailyCashLedger", "shopkeeper/CustomerUdharKhata"],
        query_type="hard_negative",
    ),
    EvaluationQuery(
        query_id="HARD-02",
        query_text="Check balance, due payments, and pending dues for customers",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/CustomerUdharKhata": 3},
        hard_negatives=["shopkeeper/SupplierContactList", "student/AssignmentTracker"],
        query_type="hard_negative",
    ),
    EvaluationQuery(
        query_id="HARD-03",
        query_text="Timer countdown for stock clearance batch discounts",
        target_domain="shopkeeper",
        relevant_components={"shopkeeper/ExpiryDateAlerts": 3},
        hard_negatives=["student/PomodoroTimer"],
        query_type="hard_negative",
    ),
    EvaluationQuery(
        query_id="HARD-04",
        query_text="Citation and formula reference catalog for college coursework",
        target_domain="student",
        relevant_components={"student/CitationGenerator": 3, "student/FormulaSheet": 3},
        hard_negatives=["shopkeeper/InventoryStockTable"],
        query_type="hard_negative",
    ),
]
