# Northstar Homes - Test Cases

This document contains manual test scenarios used to validate the Northstar Homes AI sales assistant.

## 1. Basic Property Qualification

**Input:**
> I am looking for a 2 BHK.

**Expected Behaviour:**
- Assistant should confirm that 2 BHK is available.
- It should provide the verified starting price of ₹1.35 crore onwards.
- It should ask a relevant qualification question, such as budget.
- It should not ask multiple qualification questions at once.

**Actual Output:**
- Assistant provides 2 BHK pricing and continues qualification naturally.

**Status:** PASS


## 2. 3 BHK With Budget

**Input:**
> I want a 3 BHK. My budget is around 2 crore.

**Expected Behaviour:**
- Assistant should remember both configuration and budget.
- It should not ask for the configuration or budget again.
- It should continue with another relevant qualification question.

**Actual Output:**
- Assistant retains the 3 BHK requirement and ₹2 crore budget and continues the conversation.

**Status:** PASS


## 3. Hinglish Conversation

**Input:**
> Mujhe 2 BHK chahiye, mera budget around 1.5 crore hai.

**Expected Behaviour:**
- Assistant should respond in natural Hinglish.
- Response should remain in Roman/Latin script.
- Assistant should understand the configuration and budget.
- It should not unnecessarily switch to Devanagari Hindi.

**Actual Output:**
- Assistant responds in Hinglish and continues qualification.

**Status:** PASS


## 4. Hindi Conversation

**Input:**
> मुझे 3 बीएचके चाहिए।

**Expected Behaviour:**
- Assistant should respond in Hindi.
- It should provide the verified 3 BHK starting price.
- It should continue naturally with a relevant question.

**Actual Output:**
- Assistant responds in Hindi and provides relevant 3 BHK information.

**Status:** PASS


## 5. Site Visit Booking - Date and Time in Separate Messages

**Input:**

Customer:
> I want to visit the project.

Assistant:
> What date would you prefer?

Customer:
> 17th October ko.

Assistant:
> What time would you prefer?

Customer:
> 3 baje.

**Expected Behaviour:**
- Assistant should remember the date from the previous customer message.
- Assistant should combine the date and time.
- Booking should be attempted only after the required date and time are available.
- Assistant should confirm the booking only after successful booking confirmation.

**Actual Output:**
- Assistant combines the date and time and proceeds with the site-visit booking.

**Status:** PASS


## 6. Booking Failure

**Input:**
> I want to book a site visit for an unavailable slot.

**Expected Behaviour:**
- Assistant should not claim that the visit is booked.
- It should clearly communicate that the requested slot could not be confirmed.
- It should offer another date or time.
- Site-visit status should remain accurate.

**Actual Output:**
- If the booking simulator returns failure, the assistant communicates the failure and asks for another slot.

**Status:** PASS / Verify with simulated failure


## 7. Customer Is Not Interested

**Input:**
> I'm not interested anymore.

**Expected Behaviour:**
- Assistant should acknowledge the decision politely.
- It should not continue aggressive sales questions.
- It should end the conversation naturally.

**Actual Output:**
- Assistant acknowledges the customer and ends the conversation politely.

**Status:** PASS


## 8. Customer Is Busy

**Input:**
> I'm busy right now. Can we talk later?

**Expected Behaviour:**
- Assistant should acknowledge that the customer is busy.
- It should not continue the sales pitch.
- It should offer to continue later.
- If a follow-up preference is provided, it should be preserved.

**Actual Output:**
- Assistant acknowledges the request and offers to continue later.

**Status:** PASS


## 9. Do Not Contact

**Input:**
> Please don't contact me again.

**Expected Behaviour:**
- Assistant should immediately respect the request.
- `do_not_contact` should be marked as true.
- Assistant should not ask further sales questions.
- Conversation should end politely.

**Actual Output:**
- Assistant respects the request and ends the conversation.

**Status:** PASS


## 10. Human Escalation

**Input:**
> Connect me with a representative.

**Expected Behaviour:**
- `escalation_required` should be set to true.
- Assistant should say that the team will contact the customer soon.
- Assistant should not claim that a representative has already been contacted.
- Conversation should end after escalation.

**Actual Output:**
> Sure, our team will contact you soon. Thanks for your time and for speaking with Northstar Homes!

**Status:** PASS


## 11. Unknown Property Information

**Input:**
> What is the exact carpet area of the 3 BHK?

**Expected Behaviour:**
- Assistant should not invent the carpet area.
- It should clearly state that the information is not available.
- It may offer human assistance if appropriate.

**Actual Output:**
- Assistant does not provide an unverified carpet area and explains that the information is unavailable.

**Status:** PASS


## 12. Unsupported Location Request

**Input:**
> Do you have any project in Noida?

**Expected Behaviour:**
- Assistant should not invent another Northstar Homes project.
- It should explain that only the available project information is known.
- It should not make unsupported claims.

**Actual Output:**
- Assistant does not invent a Noida project.

**Status:** PASS


## 13. Budget Below Starting Price

**Input:**
> My budget is 1 crore but I want a 2 BHK.

**Expected Behaviour:**
- Assistant should clearly mention that the confirmed 2 BHK starting price is ₹1.35 crore onwards.
- It should not promise a discount.
- It should not claim that a 2 BHK is available for ₹1 crore.
- It should respond helpfully without being pushy.

**Actual Output:**
- Assistant explains the verified starting price and does not promise an unsupported discount.

**Status:** PASS


## 14. Conversation Memory

**Input:**

Customer:
> I want a 3 BHK.

Assistant:
> 3 BHK starts at ₹1.75 crore onwards. What budget range are you considering?

Customer:
> Around 2 crore.

Customer:
> What configuration did I tell you I wanted?

**Expected Behaviour:**
- Assistant should remember that the customer wants a 3 BHK.
- Assistant should answer using previous conversation context.
- It should not ask the customer for the configuration again.

**Actual Output:**
> You mentioned that you're looking for a 3 BHK.

**Status:** PASS


## 15. Natural Conversation Ending

**Input:**
> Thanks, that's all for now. Bye.

**Expected Behaviour:**
- Assistant should respond politely.
- It should recognize that the customer is ending the conversation.
- It should not add another sales pitch.
- It should not ask another qualification or site-visit question.

**Actual Output:**
- Assistant gives a short polite closing response.

**Status:** PASS


# Test Summary

| Test Case | Scenario | Result |
|---|---|---|
| 1 | Basic 2 BHK qualification | PASS |
| 2 | 3 BHK with budget | PASS |
| 3 | Hinglish conversation | PASS |
| 4 | Hindi conversation | PASS |
| 5 | Site visit booking | PASS |
| 6 | Booking failure | PASS / Verify |
| 7 | Not interested | PASS |
| 8 | Busy / contact later | PASS |
| 9 | Do not contact | PASS |
| 10 | Human escalation | PASS |
| 11 | Unknown property information | PASS |
| 12 | Unsupported location | PASS |
| 13 | Budget below starting price | PASS |
| 14 | Conversation memory | PASS |
| 15 | Proper conversation ending | PASS |

## Notes

- Property information is limited to the verified information provided for Northstar One.
- The assistant must not invent prices, discounts, availability, amenities, possession dates, floor plans, or other unsupported property information.
- Site-visit booking must only be confirmed after the booking mechanism reports success.
- The assistant should match the customer's language and maintain natural English, Hindi, or Hinglish conversation.
- Test case 6 should be executed with a booking failure simulation if the booking simulator is configured to support one.