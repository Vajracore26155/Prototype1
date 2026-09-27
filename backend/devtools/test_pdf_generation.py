"""
Test script for PDF report generation
"""
import sys
from app.reports import generate_audit_report

def test_pdf_generation(audit_id: str):
    """Test generating a PDF report for an audit"""
    try:
        print(f"Generating PDF report for audit: {audit_id}")
        
        # Generate report
        pdf_buffer = generate_audit_report(audit_id)
        
        # Save to file for inspection
        output_file = f"test_report_{audit_id}.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✓ PDF report generated successfully!")
        print(f"✓ Saved to: {output_file}")
        print(f"✓ File size: {len(pdf_buffer.getvalue())} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test with existing audits
    test_audits = [
        "AUD-998777",  # COMPLETED audit
        "AUD-687026",  # NEEDS_REVIEW audit (with human intervention alert)
    ]
    
    print("=" * 60)
    print("PDF REPORT GENERATION TEST")
    print("=" * 60)
    print()
    
    for audit_id in test_audits:
        print(f"\nTest #{test_audits.index(audit_id) + 1}: {audit_id}")
        print("-" * 60)
        success = test_pdf_generation(audit_id)
        print()
        
        if not success:
            print("Test failed!")
            sys.exit(1)
    
    print("=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
