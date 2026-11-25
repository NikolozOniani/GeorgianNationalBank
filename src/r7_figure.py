"""Render the two distinct reserve tests in their own units."""
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def figure(outputs):
    stresses = outputs["reserve_stresses.csv"]
    public = [r for r in stresses if r["stress"]=="public_float" and r["months"]==12]
    sales = [r for r in stresses if r["stress"]=="scaled_sales" and r["months"]==12]
    frontier = [r for r in outputs["resource_frontier.csv"] if r["fx_case"]=="central" and
                r["real_discount_pct"]==3 and r["years_after_sep2026"]==5]
    with plt.rc_context({"font.family":"DejaVu Sans","svg.fonttype":"none","svg.hashsalt":"georgia-r7",
                         "axes.spines.top":False,"axes.spines.right":False,"font.size":9}):
        fig,(left,right)=plt.subplots(1,2,figsize=(12.1,5.7),gridspec_kw={"width_ratios":[1.32,1]})
        fig.subplots_adjust(left=.07,right=.97,top=.75,bottom=.25,wspace=.27)
        for rows,field,label,color,style in (
                (public,"with_purchases_usdm","With purchases","#263642","-"),
                (public,"without_purchases_usdm","Without purchases","#037564","-"),
                (public,"required_usable_usdm","Public schedule","#b75d26",":"),
                (sales,"required_usable_usdm","Public schedule + scaled sales","#825278","--")):
            left.plot([r[field]/1000 for r in rows],label=label,color=color,ls=style,lw=2)
        left.set_xticks([0,6,12,18,21],["Dec 24","Jun 25","Dec 25","Jun 26","Sep 26"])
        left.set_ylabel("USD billion")
        left.set_title("Liquid FX and twelve-month stress needs",loc="left",fontweight="bold")
        left.legend(ncol=2,loc="upper left",bbox_to_anchor=(-.02,-.16),frameon=False,fontsize=8)
        for loss,color,marker in ((.05,"#8098a4","s"),(.1,"#037564","o"),(.2,"#825278","^")):
            group=[r for r in frontier if r["loss_gdp_share"]==loss]
            right.scatter([r["assumed_annual_hazard_reduction_pp"] for r in group],
                          [r["break_even_external_return_spread_bps"] for r in group],
                          label=f"{loss:.0%} of GDP",color=color,marker=marker,s=48,zorder=3)
        right.axhline(100,color="#b75d26",ls="--",lw=1)
        right.text(.06,104,"1% annual opportunity cost",fontsize=8,color="#8c471e")
        right.set_title("Opportunity cost insurance can cover",loc="left",fontweight="bold")
        right.set_ylabel("Annual net return spread, basis points")
        right.set_xlabel("Assumed annual crisis-risk reduction, percentage points")
        right.set_xticks([0,1,2,3])
        right.legend(ncol=3,loc="upper left",bbox_to_anchor=(-.035,-.23),frameon=False,fontsize=8,
                     title="Loss if a crisis occurs")
        for ax in (left,right):
            ax.grid(axis="y",alpha=.20)
            ax.set_axisbelow(True)
        fig.suptitle("What did the additional reserves buy?",x=.07,y=.97,ha="left",fontsize=17,fontweight="bold")
        fig.text(.07,.865,"Cash coverage uses the same liquid dollars once. The insurance calculation uses a five-year horizon and the central FX case.",fontsize=10)
        buf=io.StringIO()
        fig.savefig(buf,format="svg",metadata={"Date":None,"Creator":"GeorgianNationalBank research"})
        plt.close(fig)
    return "\n".join(line.rstrip() for line in buf.getvalue().splitlines())+"\n"
