from utilities.choices import ChoiceSet

__all__ = (
    "DataFlowProtocolChoices",
    "DataFlowStatusChoices",
    "DataFlowInheritedStatusChoices",
    "TargetIsEmptyChoice",
)


class DataFlowProtocolChoices(ChoiceSet):
    """List of protocols allowed for data flows"""

    # Enable dynamic configuration
    key = "DataFlow.protocol"

    PROTOCOL_ANY = "any"
    PROTOCOL_ICMP = "icmp"
    PROTOCOL_TCP = "tcp"
    PROTOCOL_UDP = "udp"
    PROTOCOL_TCP_UDP = "tcp+udp"
    PROTOCOL_SCTP = "sctp"

    CHOICES = [
        (PROTOCOL_ANY, "Any"),
        (PROTOCOL_ICMP, "ICMP"),
        (PROTOCOL_TCP, "TCP"),
        (PROTOCOL_UDP, "UDP"),
        (PROTOCOL_TCP_UDP, "TCP+UDP"),
        (PROTOCOL_SCTP, "SCTP"),
    ]


class DataFlowStatusChoices(ChoiceSet):
    """List of statuses for data flows"""

    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"

    CHOICES = (
        (STATUS_ENABLED, "Enabled", "green"),
        (STATUS_DISABLED, "Disabled", "red"),
    )


class DataFlowInheritedStatusChoices(DataFlowStatusChoices):
    """List of statuses for data flows"""

    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"
    STATUS_INHERITED_DISABLED = "disabled-parent"

    CHOICES = (
        (STATUS_ENABLED, "Enabled", "green"),
        (STATUS_DISABLED, "Disabled", "red"),
        (STATUS_INHERITED_DISABLED, "Disabled (Inherited)", "orange"),
    )


class TargetIsEmptyChoice(ChoiceSet):
    STATUS_NULL = "true"
    STATUS_NOT_NULL = "false"

    CHOICES = (
        (STATUS_NULL, "Null"),
        (STATUS_NOT_NULL, "Not null"),
    )
