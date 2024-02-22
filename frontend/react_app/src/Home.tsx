import { BrowserRouter, Route, Router, Routes } from "react-router-dom";
import SuperTokens from "supertokens-auth-react";
import ThirdPartyEmailPassword, { Github, Google } from "supertokens-auth-react/recipe/thirdpartyemailpassword";
import EmailPassword from 'supertokens-auth-react/recipe/emailpassword'
import Session from "supertokens-auth-react/recipe/session";
import './style/Home.css'

import { SuperTokensWrapper } from "supertokens-auth-react";
import Explore from "./Explore";
import { PlayerPage } from "./PlayerPage";
import HeaderBar from "./components/HeaderBar";
import QuickPlay from "./QuickPlay";
import { validUsername } from './Validators'

export default function Home() {

	SuperTokens.init({
		appInfo: {
			apiDomain: "http://localhost:8100",
			appName: "react_app",
			websiteDomain: "http://localhost:3000"
		},
		recipeList: [
			EmailPassword.init({
				signInAndUpFeature: {
					signUpForm: {
						formFields: [
							{
								id: "username",
								label: "Unique Username",
								validate: validUsername
							}
						]
					}
				}
			}),
			Session.init({
				// sessionTokenBackendDomain: ".some.domain.com" 
				// If multi domain is set on the backend, this field should
				// have the same value.
			})

		]
	});

	async function onEmailLogin(context: ThirdPartyEmailPassword.OnHandleEventContext) {
		console.log("Handling onEmailLogin.")
		if (context.action === "SESSION_ALREADY_EXISTS") {

		} else if (context.action === "SUCCESS") {

			console.log("Authentication success, doing print request.")

		}
	}

	return (

		<SuperTokensWrapper>
			<HeaderBar />

			<BrowserRouter>
				<Routes>
					<Route path="/" element={<Explore />} />
					<Route path="/watch:streamer" element={<PlayerPage user={null} />} />
					<Route path="/play" element={<QuickPlay />} />
				</Routes>
			</BrowserRouter>
		</SuperTokensWrapper >

	)
}