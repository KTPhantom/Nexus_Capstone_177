SCENARIOS = [
    # Student
    {"id": "STU-01", "query": "I need to study for exams and track my grades", "domain": "student", "expected_tools": ["PomodoroTimer", "GradeTracker"], "min_tools": 2, "max_tools": 4},
    {"id": "STU-02", "query": "GATE prep with formulas and flashcards", "domain": "student", "expected_tools": ["FormulaSheet", "FlashcardDeck"], "min_tools": 2, "max_tools": 3},
    {"id": "STU-03", "query": "Track my college attendance", "domain": "student", "expected_tools": ["AttendanceTracker"], "min_tools": 1, "max_tools": 2},
    {"id": "STU-04", "query": "Group project assignments and notes", "domain": "student", "expected_tools": ["AssignmentTracker", "NotesEditor"], "min_tools": 2, "max_tools": 4},
    {"id": "STU-05", "query": "Writing research papers and generating citations", "domain": "student", "expected_tools": ["NotesEditor", "CitationGenerator"], "min_tools": 2, "max_tools": 3},
    {"id": "STU-06", "query": "Formula revision for math", "domain": "student", "expected_tools": ["FormulaSheet"], "min_tools": 1, "max_tools": 2},
    {"id": "STU-07", "query": "Learning new language with flashcards", "domain": "student", "expected_tools": ["FlashcardDeck"], "min_tools": 1, "max_tools": 2},
    {"id": "STU-08", "query": "GPA optimization and exam tracking", "domain": "student", "expected_tools": ["GradeTracker", "AssignmentTracker"], "min_tools": 2, "max_tools": 3},
    # Shopkeeper
    {"id": "SHP-01", "query": "Manage small grocery store inventory", "domain": "shopkeeper", "expected_tools": ["InventoryStockTable"], "min_tools": 1, "max_tools": 2},
    {"id": "SHP-02", "query": "Wholesale distributor supplier list", "domain": "shopkeeper", "expected_tools": ["SupplierContactList"], "min_tools": 1, "max_tools": 2},
    {"id": "SHP-03", "query": "Morning cash opening and daily ledger", "domain": "shopkeeper", "expected_tools": ["DailyCashLedger"], "min_tools": 1, "max_tools": 2},
    {"id": "SHP-04", "query": "Ordering from suppliers and checking expiry", "domain": "shopkeeper", "expected_tools": ["SupplierContactList", "ExpiryDateAlerts"], "min_tools": 2, "max_tools": 3},
    {"id": "SHP-05", "query": "Expiry stock management", "domain": "shopkeeper", "expected_tools": ["ExpiryDateAlerts", "InventoryStockTable"], "min_tools": 2, "max_tools": 3},
    {"id": "SHP-06", "query": "Barcode POS checkout and daily sales", "domain": "shopkeeper", "expected_tools": ["BarcodeScannerInput", "DailySalesReceipt"], "min_tools": 2, "max_tools": 3},
    {"id": "SHP-07", "query": "Monthly profit analysis", "domain": "shopkeeper", "expected_tools": ["ProfitMarginCalculator"], "min_tools": 1, "max_tools": 2},
    {"id": "SHP-08", "query": "Credit customer tracking udhar khata", "domain": "shopkeeper", "expected_tools": ["CustomerUdharKhata"], "min_tools": 1, "max_tools": 2},
    # Mixed
    {"id": "MIX-01", "query": "Student with part-time shop work tracking cash and grades", "domain": "mixed", "expected_tools": ["DailyCashLedger", "GradeTracker"], "min_tools": 2, "max_tools": 4},
    {"id": "MIX-02", "query": "General productivity timer and sales", "domain": "mixed", "expected_tools": ["PomodoroTimer", "DailySalesReceipt"], "min_tools": 2, "max_tools": 4},
    {"id": "MIX-03", "query": "Multi-domain workspace for supplier and notes", "domain": "mixed", "expected_tools": ["SupplierContactList", "NotesEditor"], "min_tools": 2, "max_tools": 4},
    {"id": "MIX-04", "query": "Track attendance and udhar khata", "domain": "mixed", "expected_tools": ["AttendanceTracker", "CustomerUdharKhata"], "min_tools": 2, "max_tools": 4},
]
