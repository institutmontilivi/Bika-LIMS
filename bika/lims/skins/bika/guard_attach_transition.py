## Script (Python) "guard_attach_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

workflow = context.portal_workflow

# Can't do anything to the object if it's cancelled
# reference and duplicate analyses don't have cancellation_state
#if context.portal_type == "Analysis":
if workflow.getInfoFor(context, 'cancellation_state', 'active') == "cancelled":
    return False

# All kinds of analyses get their AttachmentOption checked
# more thorough than strictly needed.
if context.portal_type in ("Analysis",
                           "ReferenceAnalysis",
                           "DuplicateAnalysis"):
    if not context.getAttachment():
        service = context.getService()
        if service.getAttachmentOption() == 'r':
            return False

# only Analysis objects need their dependencies checked
if context.portal_type == "Analysis":
    dependencies = context.getDependencies()
    for dep in dependencies:
        review_state = workflow.getInfoFor(dep, 'review_state')
        if review_state in ('to_be_sampled', 'to_be_preserved',
                                'sample_due', 'sample_received',
                                'attachment_due'):
            return False

if context.portal_type == "AnalysisRequest":
    # Allow transition to 'to_be_verified'
    # if all analyses are at least to_be_verified
    for a in context.objectValues('Analysis'):
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('to_be_sampled', 'to_be_preserved', 'sample_due',
                            'sample_received', 'attachment_due'):
            return False

if context.portal_type == "Worksheet":
    # Allow transition to 'to_be_verified'
    # if all analyses are at least to_be_verified
    for a in context.getAnalyses():
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('to_be_sampled', 'to_be_preserved', 'sample_due',
                            'sample_received', 'attachment_due', 'assigned'):
            # Note: referenceanalyses and duplicateanalysis can
            # still have review_state = "assigned".
            return False

return True
