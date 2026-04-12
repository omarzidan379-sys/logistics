# Customer Quotation Approval - User Guide

## 📖 For Customers (Portal Users)

### How to View Your Quotations

1. **Login to Portal**
   - Go to your company's freight portal
   - Enter your email and password
   - Click "Sign In"

2. **Navigate to Quotations**
   - Click "Quotations" in the menu
   - Or go to: `/my/quotations`

3. **View Quotation List**
   - See all your quotations
   - Filter by status (All, Draft, Quoted, Accepted, Rejected)
   - Sort by date, reference, or validity

### How to Review a Quotation

1. **Click on Quotation**
   - Click the quotation number or row
   - Quotation detail page opens

2. **Review Information**
   - **Header**: Quotation number and route
   - **Status**: Current status badge
   - **Key Info**: Date, validity, service type, direction
   - **Route**: Origin and destination with addresses
   - **Cargo**: Description, weight, volume, container details
   - **Pricing**: Detailed breakdown of all charges
   - **Terms**: Terms and conditions

3. **Check Validity**
   - Look at "Valid Until" date
   - Quotation expires after this date
   - Contact sales if you need extension

### How to Accept a Quotation

1. **Verify Status**
   - Status must be "Awaiting Response" (yellow badge)
   - Accept and Reject buttons visible

2. **Click "Accept Quotation"**
   - Green button on the left
   - Confirmation dialog appears

3. **Confirm**
   - Click "OK" to confirm
   - Button shows "Processing..."
   - Success message appears

4. **After Acceptance**
   - Status changes to "Accepted" (green badge)
   - Buttons disappear
   - Action date displayed
   - Sales team notified automatically
   - You'll receive booking confirmation soon

### How to Reject a Quotation

1. **Click "Reject Quotation"**
   - Red button on the right
   - Modal window opens

2. **Provide Reason (Optional)**
   - Type your reason for rejection
   - Examples:
     - "Price too high"
     - "Delivery time not suitable"
     - "Found alternative supplier"
     - "Requirements changed"
   - This helps us improve our service

3. **Confirm Rejection**
   - Click "Confirm Rejection"
   - Modal closes
   - Success message appears

4. **After Rejection**
   - Status changes to "Rejected" (red badge)
   - Buttons disappear
   - Your reason displayed
   - Sales team notified
   - They may contact you to discuss

### How to Download Quotation PDF

1. **Scroll to Bottom**
   - Find "Download PDF" button
   - Black button with download icon

2. **Click Button**
   - PDF generates automatically
   - Downloads to your device

3. **Use PDF**
   - Print for records
   - Share with colleagues
   - Attach to emails

### Understanding Status Badges

| Badge | Color | Meaning |
|-------|-------|---------|
| Draft | Gray | Being prepared by sales team |
| Awaiting Response | Yellow | Waiting for your decision |
| Accepted | Green | You approved this quotation |
| Rejected | Red | You declined this quotation |
| Expired | Gray | Validity date passed |
| Cancelled | Dark Gray | Cancelled by sales team |

### Email Notifications

You'll receive emails for:
- ✉️ New quotation sent
- ✅ Quotation accepted (confirmation)
- ❌ Quotation rejected (confirmation)
- 📦 Booking confirmed
- 🚢 Shipment updates

**Manage Notifications:**
1. Go to Portal Settings
2. Toggle notification types
3. Choose frequency (realtime/daily/weekly)

### Tips for Customers

✅ **Do:**
- Review quotations promptly
- Check validity dates
- Provide rejection reasons
- Download PDFs for records
- Contact sales with questions

❌ **Don't:**
- Wait until last minute
- Accept without reviewing
- Ignore expired quotations
- Share login credentials

### Common Questions

**Q: Can I negotiate the price?**
A: Contact your sales representative directly to discuss pricing.

**Q: What happens after I accept?**
A: Sales team will create a booking and send you confirmation with vessel/flight details.

**Q: Can I change my mind after accepting?**
A: Contact sales immediately. Early cancellation may be possible.

**Q: Why can't I see Accept/Reject buttons?**
A: Buttons only appear for quotations in "Awaiting Response" status.

**Q: How long is a quotation valid?**
A: Check the "Valid Until" date. Typically 30 days from quotation date.

**Q: Can I accept a quotation after it expires?**
A: No, contact sales for a new quotation with updated pricing.

---

## 📊 For Sales Team (Internal Users)

### How to Send a Quotation

1. **Create Quotation**
   - Go to Freight → Quotations
   - Click "Create"
   - Fill in all required fields
   - Add quotation lines with pricing

2. **Review Before Sending**
   - Check profit margin
   - Verify pricing accuracy
   - Review terms and conditions
   - Set appropriate validity date

3. **Send to Customer**
   - Click "Send" button
   - State changes to "Quoted"
   - Email sent automatically
   - Customer receives portal link

### Monitoring Quotations

**Dashboard View:**
- Draft: Quotations being prepared
- Quoted: Awaiting customer response
- Accepted: Customer approved
- Rejected: Customer declined

**Key Metrics:**
- Acceptance rate
- Average response time
- Rejection reasons
- Conversion to bookings

### Handling Customer Actions

**When Customer Accepts:**
1. Email notification received
2. Review quotation details
3. Create booking
4. Coordinate with operations
5. Send booking confirmation

**When Customer Rejects:**
1. Email notification received
2. Review rejection reason
3. Contact customer to discuss
4. Consider revising quotation
5. Send new quotation if appropriate

### Best Practices

✅ **Do:**
- Send quotations promptly
- Set realistic validity dates
- Follow up on pending quotations
- Analyze rejection reasons
- Maintain customer communication
- Create bookings quickly after acceptance

❌ **Don't:**
- Send quotations with errors
- Set too short validity periods
- Ignore rejected quotations
- Delay booking creation
- Forget to follow up

### Workflow Optimization

**Standard Flow:**
```
RFQ → Price → Send (Quoted) → Customer Accepts → Create Booking → Shipment
```

**If Rejected:**
```
Rejected → Review Reason → Contact Customer → Revise → Send New Quote
```

**Multi-Modal:**
```
Accepted → Create Multi-Modal Shipment → Multiple Transport Legs
```

### Email Templates

**Quotation Sent:**
- Modern design
- All quotation details
- Portal link
- Professional footer

**Quotation Accepted:**
- Green success theme
- Customer information
- Action timestamp
- Next steps reminder

**Quotation Rejected:**
- Red rejection theme
- Rejection details
- Customer feedback
- Recommended actions

### Reports & Analytics

**Available Reports:**
1. Quotation Analysis
   - Acceptance rate by customer
   - Acceptance rate by route
   - Average response time
   - Rejection reasons

2. Pricing Effectiveness
   - Win rate by price range
   - Competitor comparison
   - Margin analysis

3. Customer Behavior
   - Response patterns
   - Preferred routes
   - Booking frequency

### Troubleshooting

**Customer Can't See Quotation:**
- Check portal access granted
- Verify email address correct
- Check quotation partner matches
- Resend portal invitation

**Customer Can't Accept:**
- Verify state is "Quoted"
- Check validity date not passed
- Verify customer logged in
- Check browser compatibility

**Email Not Received:**
- Check spam folder
- Verify email address
- Check outgoing mail server
- Resend manually

**Buttons Not Working:**
- Check browser console
- Clear browser cache
- Try different browser
- Check Odoo logs

### Integration with Other Modules

**Booking Module:**
- Auto-create booking from accepted quotation
- Link quotation to booking
- Transfer all details

**Shipment Module:**
- Create shipment from booking
- Track shipment progress
- Update customer automatically

**Accounting Module:**
- Generate invoice from booking
- Link to quotation
- Track payments

**CRM Module:**
- Track opportunities
- Link quotations to leads
- Measure conversion rates

---

## 🎓 Training Resources

### Video Tutorials
- Creating and sending quotations
- Customer portal walkthrough
- Handling acceptances and rejections
- Creating bookings from quotations

### Documentation
- Full implementation guide
- Technical documentation
- API reference
- Troubleshooting guide

### Support
- Email: support@yourcompany.com
- Phone: +1-XXX-XXX-XXXX
- Portal: support.yourcompany.com
- Hours: Mon-Fri 9AM-5PM

---

## 📞 Contact Information

**For Customers:**
- Sales Team: sales@yourcompany.com
- Customer Service: service@yourcompany.com
- Emergency: +1-XXX-XXX-XXXX

**For Internal Users:**
- IT Support: it@yourcompany.com
- System Admin: admin@yourcompany.com
- Training: training@yourcompany.com

---

## 🔄 Version History

### Version 1.0.0 (Current)
- Initial release
- Customer acceptance/rejection
- Modern portal UI
- Email notifications
- Mobile support

---

**Need Help?** Contact your sales representative or support team!
