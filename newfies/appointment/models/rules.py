from django.db import models
from django.utils.translation import ugettext_lazy as _
from dateutil import rrule

freqs = (
    ("YEARLY", _("Yearly")),
    ("MONTHLY", _("Monthly")),
    ("WEEKLY", _("Weekly")),
    ("DAILY", _("Daily")),
    ("HOURLY", _("Hourly")),
    ("MINUTELY", _("Minutely")),
    ("SECONDLY", _("Secondly"))
)


class Rule(models.Model):
    """
    This defines a rule by which an event will recur.  This is defined by the
    rrule in the dateutil documentation.

    * name - the human friendly name of this kind of recursion.
    * description - a short description describing this type of recursion.
    * frequency - the base recurrence period
    * param - extra params required to define this type of recursion. The params
      should follow this format:

        param = [rruleparam:value;]*
        rruleparam = see list below
        value = int[,int]*

      The options are: (documentation for these can be found at
      http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57)
        ** count
        ** bysetpos
        ** bymonth
        ** bymonthday
        ** byyearday
        ** byweekno
        ** byweekday
        ** byhour
        ** byminute
        ** bysecond
        ** byeaster
    """
    name = models.CharField(verbose_name=_("name"), max_length=32)
    description = models.TextField(verbose_name=_("description"))
    frequency = models.CharField(verbose_name=_("frequency"), choices=freqs,
                                 max_length=10)
    params = models.TextField(verbose_name=_("params"), null=True, blank=True,
                              help_text=_("example : count:1;bysecond:3;"))

    class Meta:
        verbose_name = _('rule')
        verbose_name_plural = _('rules')
        app_label = "appointment"

    def get_params(self):
        """
        >>> rule = Rule(params = "count:1;bysecond:1;byminute:1,2,4,5")
        >>> rule.get_params()
        {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}

        >>> rule = Rule(params = "count:1;bysecond:3;byweekday:TU,WE,TH")
        >>> rule.get_params()
        {'bysecond': 1, 'byweekday': (TU, WE, TH), 'count': 1}
        """
        if self.params is None:
            return {}

        # remove "" from self.params
        params = self.params.replace('"', '')

        params = params.split(';')
        param_dict = []
        for param in params:
            param = param.split(':')
            if len(param) == 2:

                temp_list = []
                tuple_flag = False
                for p in param[1].split(','):
                    if p.isdigit():
                        temp_list.append(int(p))
                    else:
                        tuple_flag = True
                        temp_list.append(eval('rrule.%s' % str(p)))

                if tuple_flag:
                    temp_list = tuple(temp_list)

                param = (str(param[0]), temp_list)
                if len(param[1]) == 1:
                    param = (param[0], param[1][0])
                param_dict.append(param)
        return dict(param_dict)

    def __unicode__(self):
        """Human readable string for Rule"""
        return 'Rule %s params %s' % (self.name, self.params)
