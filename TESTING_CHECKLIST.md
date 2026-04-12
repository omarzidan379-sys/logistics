# Quotation Approval System - Testing Checklist

## 🧪 Quick Testing Guide

### Pre-requisites
- [ ] Odoo 17 instance running
- [ ] Freight Management module installed/upgraded
- [ ] Test customer with portal access
- [ ] Outgoing mail server configured
- [ ] Test quotation with pricing

---

## 1️⃣ Backend Testing

### Model & Business Logic

- [ ] **Create Quotation**
  - Create new quotation in draft state
  - Add quotation lines with pricing
  - Verify total amount calculates correctly

- [ ] **Send Quotation**
  - Click "Send" button
  - Verify state changes to 'quoted'
  - Check email sent to customer
  - Verify portal link in email works

- [ ] **State Transitions**
  - Verify only 'quoted' quotations can be accepted/rejected
  - Try accepting draft quotation (should fail)
  - Try accepting expired quotation (should fail)

- [ ] **Security**
  - Login as different portal user
  - Try to accept quotation (should fail with AccessError)
  - Verify only linked customer can act

---

## 2️⃣ Portal UI Testing

### Visual & Layout

- [ ] **Quotation List Page** (`/my/quotations`)
  - All quotations display correctly
  - Filters work (All, Draft, Quoted, Accepted, Rejected)
  - Sorting works (Date, Reference, Valid Until)
  - Pagination works

- [ ] **Quotation Detail Page** (`/my/quotations/<id>`)
  - Modern UI loads correctly
  - All sections visible:
    - [ ] Header with quotation number
    - [ ] Status badge (correct color)
    - [ ] Action buttons (if quoted)
    - [ ] Info grid (4 cards)
    - [ ] Route display (origin → destination)
    - [ ] Cargo details
    - [ ] Pricing table
    - [ ] Terms & conditions
    - [ ] Download button

- [ ] **Status Badges**
  - Draft: Gray
  - Quoted: Yellow
  - Accepted: Green
  - Rejected: Red
  - Expired: Gray
  - Cancelled: Dark gray

- [ ] **Responsive Design**
  - Desktop view (1920px)
  - Tablet view (768px)
  - Mobile view (375px)
  - No horizontal scroll
  - Touch-friendly buttons

---

## 3️⃣ Accept Flow Testing

### Happy Path

- [ ] **Initial State**
  - Quotation in 'quoted' state
  - Accept button visible and enabled
  - Reject button visible and enabled

- [ ] **Click Accept**
  - Confirmation dialog appears
  - Click "OK"
  - Button shows loading state
  - Success alert appears
  - Page reloads automatically

- [ ] **After Accept**
  - Status badge shows "Accepted" (green)
  - Action buttons hidden
  - Customer action date displayed
  - Chatter shows acceptance log
  - Sales team receives email

- [ ] **Email to Sales Team**
  - Subject: "✅ Quotation XXX Accepted by Customer"
  - Green theme
  - Customer information correct
  - Action timestamp correct
  - Total amount correct
  - Link to backend works

### Edge Cases

- [ ] **Double Accept**
  - Try accepting already accepted quotation
  - Should show error message

- [ ] **Network Error**
  - Simulate network failure
  - Error message displays
  - Button re-enables

---

## 4️⃣ Reject Flow Testing

### Happy Path

- [ ] **Initial State**
  - Quotation in 'quoted' state
  - Reject button visible and enabled

- [ ] **Click Reject**
  - Modal opens
  - Reason textarea visible
  - Cancel button works
  - Confirm button enabled

- [ ] **Enter Reason**
  - Type rejection reason
  - Reason saves correctly

- [ ] **Confirm Rejection**
  - Modal closes
  - Success alert appears
  - Page reloads automatically

- [ ] **After Reject**
  - Status badge shows "Rejected" (red)
  - Action buttons hidden
  - Customer action date displayed
  - Rejection reason displayed
  - Chatter shows rejection log with reason
  - Sales team receives email

- [ ] **Email to Sales Team**
  - Subject: "❌ Quotation XXX Rejected by Customer"
  - Red theme
  - Customer information correct
  - Action timestamp correct
  - Rejection reason included
  - Link to backend works

### Edge Cases

- [ ] **Reject Without Reason**
  - Leave reason blank
  - Should still work (reason optional)

- [ ] **Double Reject**
  - Try rejecting already rejected quotation
  - Should show error message

- [ ] **Cancel Modal**
  - Open reject modal
  - Click cancel
  - Modal closes
  - No action taken

---

## 5️⃣ Email Testing

### Quotation Sent Email

- [ ] **Recipient**
  - Sent to customer email
  - From salesperson email

- [ ] **Content**
  - Subject correct
  - Customer name correct
  - Quotation details correct
  - Route information correct
  - Total amount correct
  - Valid until date correct

- [ ] **Links**
  - Portal link works
  - Opens quotation detail page
  - Customer can login if needed

- [ ] **Design**
  - Modern gradient header
  - Professional layout
  - Mobile-friendly
  - Images load (if any)

### Acceptance Email

- [ ] **Recipient**
  - Sent to salesperson
  - CC to sales manager (if configured)

- [ ] **Content**
  - Subject has ✅ emoji
  - Customer name correct
  - Route correct
  - Acceptance timestamp correct
  - Total amount correct
  - Next steps listed

- [ ] **Links**
  - Backend link works
  - Opens quotation in Odoo

### Rejection Email

- [ ] **Recipient**
  - Sent to salesperson
  - CC to sales manager (if configured)

- [ ] **Content**
  - Subject has ❌ emoji
  - Customer name correct
  - Route correct
  - Rejection timestamp correct
  - Rejection reason displayed (if provided)
  - Recommended actions listed

- [ ] **Links**
  - Backend link works
  - Opens quotation in Odoo

---

## 6️⃣ Mobile Testing

### iOS Safari

- [ ] Layout responsive
- [ ] Buttons touch-friendly
- [ ] Modal works
- [ ] No zoom issues
- [ ] Smooth scrolling

### Android Chrome

- [ ] Layout responsive
- [ ] Buttons touch-friendly
- [ ] Modal works
- [ ] No zoom issues
- [ ] Smooth scrolling

### Common Mobile Checks

- [ ] Text readable without zoom
- [ ] Buttons minimum 44x44px
- [ ] No horizontal scroll
- [ ] Tables scroll horizontally if needed
- [ ] Forms easy to fill

---

## 7️⃣ Browser Compatibility

### Chrome (Latest)
- [ ] All features work
- [ ] CSS renders correctly
- [ ] JavaScript executes
- [ ] No console errors

### Firefox (Latest)
- [ ] All features work
- [ ] CSS renders correctly
- [ ] JavaScript executes
- [ ] No console errors

### Safari (Latest)
- [ ] All features work
- [ ] CSS renders correctly
- [ ] JavaScript executes
- [ ] No console errors

### Edge (Latest)
- [ ] All features work
- [ ] CSS renders correctly
- [ ] JavaScript executes
- [ ] No console errors

---

## 8️⃣ Performance Testing

- [ ] **Page Load Time**
  - Quotation list loads < 2 seconds
  - Quotation detail loads < 2 seconds

- [ ] **Action Response Time**
  - Accept action completes < 3 seconds
  - Reject action completes < 3 seconds

- [ ] **Email Delivery**
  - Emails sent within 1 minute
  - No emails in failed queue

---

## 9️⃣ Security Testing

### Authorization

- [ ] **Portal User A**
  - Can view own quotations
  - Can accept own quotations
  - Can reject own quotations

- [ ] **Portal User B**
  - Cannot view User A's quotations
  - Cannot accept User A's quotations
  - Cannot reject User A's quotations

- [ ] **Public User**
  - Cannot access quotation pages
  - Redirected to login

### State Validation

- [ ] Cannot accept draft quotation
- [ ] Cannot accept accepted quotation
- [ ] Cannot accept rejected quotation
- [ ] Cannot accept expired quotation
- [ ] Cannot accept cancelled quotation

### Input Validation

- [ ] Rejection reason accepts text
- [ ] Rejection reason handles special characters
- [ ] Rejection reason handles long text (>1000 chars)
- [ ] XSS protection (try `<script>alert('xss')</script>`)

---

## 🔟 Integration Testing

### Booking Creation

- [ ] **After Accept**
  - Create booking button appears
  - Click create booking
  - Booking created with correct data
  - Booking linked to quotation

### Shipment Creation

- [ ] **From Accepted Quotation**
  - Create shipment button appears
  - Click create shipment
  - Shipment created with correct data
  - Shipment linked to quotation

### Multi-Modal

- [ ] **Multi-Modal Quotation**
  - Mark quotation as multi-modal
  - Accept quotation
  - Create multi-modal shipment
  - Multiple transport legs created

---

## 1️⃣1️⃣ Accessibility Testing

- [ ] **Keyboard Navigation**
  - Tab through all elements
  - Enter/Space activates buttons
  - Escape closes modal

- [ ] **Screen Reader**
  - All images have alt text
  - Buttons have aria-labels
  - Form fields have labels
  - Status announced

- [ ] **Color Contrast**
  - Text readable on backgrounds
  - Meets WCAG AA standards
  - Color not sole indicator

---

## 1️⃣2️⃣ Error Handling

### Network Errors

- [ ] **Offline**
  - Try action while offline
  - Error message displays
  - User can retry

- [ ] **Timeout**
  - Simulate slow connection
  - Loading state shows
  - Timeout handled gracefully

### Server Errors

- [ ] **500 Error**
  - Simulate server error
  - Error message displays
  - User informed

- [ ] **403 Error**
  - Try unauthorized action
  - Access denied message
  - User redirected

### Validation Errors

- [ ] **Invalid State**
  - Try invalid action
  - Validation message displays
  - User informed of requirement

---

## 1️⃣3️⃣ Data Integrity

- [ ] **Audit Trail**
  - All actions logged in chatter
  - Timestamps recorded
  - User information captured

- [ ] **Database**
  - State changes persisted
  - Dates saved correctly
  - Reasons saved correctly

- [ ] **Concurrent Access**
  - Two users view same quotation
  - One accepts
  - Other sees updated state

---

## 1️⃣4️⃣ Regression Testing

- [ ] **Existing Features**
  - Quotation creation still works
  - Quotation editing still works
  - Quotation PDF generation works
  - Other portal pages work

- [ ] **Backend**
  - Quotation form view works
  - Quotation list view works
  - Quotation reports work
  - Dashboard works

---

## ✅ Sign-Off

### Tested By
- Name: _______________
- Date: _______________
- Environment: _______________

### Issues Found
- [ ] No issues
- [ ] Issues logged (see issue tracker)

### Approval
- [ ] Ready for production
- [ ] Needs fixes

### Notes
```
_______________________________________
_______________________________________
_______________________________________
```

---

## 🚀 Production Deployment Checklist

- [ ] All tests passed
- [ ] Database backup created
- [ ] Module upgraded successfully
- [ ] Email server tested
- [ ] Portal users notified
- [ ] Documentation updated
- [ ] Support team trained
- [ ] Monitoring configured
- [ ] Rollback plan ready

---

**Testing Complete!** 🎉
